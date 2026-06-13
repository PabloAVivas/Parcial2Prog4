import uuid
import logging
from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from app.core.config import settings
from app.modules.pago.models import Pago
from app.modules.pedido.models import Pedido
from app.modules.pago.schemas import PagoCrearResponse, PagoEstadoResponse
from app.modules.pago.unit_of_work import PagoUnitOfWork
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class PagoService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_mp_access_token(self) -> Optional[str]:
        return settings.MP_ACCESS_TOKEN

    def _get_mp_public_key(self) -> Optional[str]:
        return settings.MP_PUBLIC_KEY

    def _crear_preferencia_mp(self, transaction_amount: float, titulo: str, pedido_id: int, back_urls: dict) -> dict:
        access_token = self._get_mp_access_token()
        if not access_token:
            raise RuntimeError(
                "MercadoPago no está configurado. Configure MP_ACCESS_TOKEN"
            )

        try:
            import mercadopago
            sdk = mercadopago.SDK(access_token)

            preference_data = {
                "items": [{
                    "title": titulo,
                    "quantity": 1,
                    "unit_price": float(transaction_amount),
                    "currency_id": "ARS",
                }],
                "external_reference": str(pedido_id),
                "back_urls": back_urls,
                "notification_url": (settings.MP_WEBHOOK_URL or f"{settings.VITE_API_URL}/api/v1/pagos/webhook"),
                "auto_return": "approved",
            }

            result = sdk.preference().create(preference_data)

            if result.get("status") not in (200, 201):
                logger.error("Error creando preferencia MP: %s", result)
                raise RuntimeError(
                    "Error al crear preferencia: "
                    f"{result.get('response', {}).get('message', 'desconocido')}"
                )

            response = result.get("response", {})
            return {
                "preference_id": response.get("id"),
                "init_point": response.get("init_point"),
                "external_reference": response.get("external_reference"),
            }

        except ImportError:
            raise RuntimeError("pip install mercadopago")
        except Exception as e:
            logger.exception("Error inesperado al crear preferencia MP")
            raise RuntimeError(f"Error de conexión con MP: {str(e)}")

    def _consultar_pago_mp(self, payment_id: int) -> dict:
        access_token = self._get_mp_access_token()
        if not access_token:
            raise RuntimeError("MP no configurado")

        try:
            import mercadopago
            sdk = mercadopago.SDK(access_token)
            result = sdk.payment().get(payment_id)

            if result.get("status") != 200:
                logger.error("Error consultando pago MP %s: %s", payment_id, result)
                raise RuntimeError(f"Error al consultar pago {payment_id}")

            response = result.get("response", {})
            return {
                "mp_payment_id":        response.get("id"),
                "mp_status":            response.get("status"),
                "mp_status_detail":     response.get("status_detail"),
                "external_reference": response.get("external_reference"),
                "payment_method_id":    response.get("payment_method_id"),
            }

        except ImportError:
            raise RuntimeError("pip install mercadopago")
        except Exception as e:
            logger.exception("Error consultando pago MP %s", payment_id)
            raise RuntimeError(f"Error de conexión con MP: {str(e)}")


    def crear_pago(self, pedido_id: int) -> PagoCrearResponse:
        pedido = self._session.get(Pedido, pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        if not self._get_mp_access_token():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MercadoPago no configurado. Configure MP_ACCESS_TOKEN",
            )
        ngrok_url = settings.NGROK_URL or "http://localhost:8000"
        back_urls = {
            "success": f"{ngrok_url}/api/v1/pagos/redirect/{pedido_id}/success",
            "failure": f"{ngrok_url}/api/v1/pagos/redirect/{pedido_id}/failure",
            "pending": f"{ngrok_url}/api/v1/pagos/redirect/{pedido_id}/pending",
        }

        try:
            mp_data = self._crear_preferencia_mp(
                transaction_amount=pedido.total,
                titulo=f"Pedido #{pedido_id} - FoodStore",
                pedido_id=pedido_id,
                back_urls=back_urls,
            )
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        with PagoUnitOfWork(self._session) as uow:
            pago = Pago(
                pedido_id=pedido_id,
                external_reference= mp_data["external_reference"],
                idempotency_key=str(uuid.uuid4()),
                transaction_amount=pedido.total,
            )
            uow.pago.add(pago)

            return PagoCrearResponse(
                pago_id=pago.id,
                preference_id=mp_data["preference_id"],
                init_point=mp_data.get("init_point"),
                public_key=self._get_mp_public_key(),
            )

    def procesar_webhook(self, data: dict, query_params: Optional[dict] = None) -> dict:
        logger.info("Webhook recibido: data=%s qs=%s", data, query_params or {})
        if not data and query_params:
            data = query_params

        topic = data.get("type") or data.get("topic")
        data_id = data.get("data_id") or (data.get("data") or {}).get("id")
        payment_id = data.get("id")

        if not data_id and query_params:
            data_id = query_params.get("data.id") or query_params.get("id")
        if not topic and query_params:
            topic = query_params.get("topic") or query_params.get("type")

        pago_mp_id = payment_id or data_id
        if not pago_mp_id:
            return {"status": "ignored", "reason": "No payment ID"}
        if topic not in (None, "payment", "merchant_order"):
            return {"status": "ignored", "reason": f"Topic: {topic}"}
        try:
            mp_info = self._consultar_pago_mp(int(pago_mp_id))
            estado_mp = mp_info.get("mp_status")
            if estado_mp == "approved":
                nuevo_estado = "aprobado"
            elif estado_mp in ("rejected", "cancelled", "refunded", "charged_back"):
                nuevo_estado = "rechazado"
            elif estado_mp in ("pending", "in_process", "authorized"):
                nuevo_estado = "pendiente"
            else:
                return {"status": "ignored", "reason": f"Unknown status: {estado_mp}"}

            with PagoUnitOfWork(self._session) as uow:
                pago = uow.pago.get_by_mp_payment_id(int(pago_mp_id))
                if not pago:
                    ext_ref = mp_info.get("external_reference")
                    pago = uow.pago.get_by_external_reference(ext_ref)
                if not pago:
                    return {"status": "ignored", "reason": "Pago not found in local DB"}
                if pago.mp_status is not None and pago.mp_status not in ("pending", "in_process", "authorized"):
                    return {"status": "already_processed",
                            "estado": pago.mp_status}

                pago.mp_payment_id = int(pago_mp_id)
                pago.mp_status = estado_mp
                pago.mp_status_detail = mp_info.get("mp_status_detail")
                pago.payment_method_id = mp_info.get("payment_method_id")
                uow.pago.add(pago)
                pedido = uow.pedido.get_by_id(pago.pedido_id)
                if nuevo_estado == "aprobado":
                    pedido.estado_codigo = "CONFIRMADO"
                    uow.pedido.add(pedido)
                elif nuevo_estado == "rechazado":
                    pedido.estado_codigo = "CANCELADO"
                    uow.pedido.add(pedido)

            return {
                "status": "processed",
                "pago_id": pago.id,
                "estado": nuevo_estado,
                "pedido_id": pago.pedido_id,
            }

        except Exception as e:
            logger.exception("Error procesando webhook MP")
            return {"status": "error", "reason": str(e)}

    def confirmar_pago(self, pedido_id: int, payment_id: Optional[int] = None) -> PagoEstadoResponse:
        pedido = self._session.get(Pedido, pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        resolved_payment_id = payment_id
        if not resolved_payment_id:
            with PagoUnitOfWork(self._session) as uow:
                pago_local = uow.pago.get_ultimo_by_pedido(pedido_id)
                if pago_local and pago_local.mp_payment_id:
                    resolved_payment_id = pago_local.mp_payment_id

        if resolved_payment_id:
            try:
                mp_info = self._consultar_pago_mp(resolved_payment_id)
            except RuntimeError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e),
                )

            estado_mp = mp_info.get("mp_status")
            if estado_mp == "approved":
                nuevo_estado = "aprobado"
            elif estado_mp in ("rejected", "cancelled", "refunded", "charged_back"):
                nuevo_estado = "rechazado"
            else:
                nuevo_estado = "pendiente"

            with PagoUnitOfWork(self._session) as uow:
                pago = uow.pago.get_by_mp_payment_id(resolved_payment_id)
                if not pago:
                    pago = uow.pago.get_ultimo_by_pedido(pedido_id)

                if pago:
                    pago.mp_payment_id = resolved_payment_id
                    pago.mp_status = estado_mp
                    pago.mp_status_detail = mp_info.get("mp_status_detail")
                    pago.payment_method_id = mp_info.get("payment_method_id")
                    uow.pago.add(pago)

                    if nuevo_estado == "aprobado":
                        pedido.estado_codigo = "CONFIRMADO"
                        uow.pedido.add(pedido)
                    elif nuevo_estado == "rechazado":
                        pedido.estado_codigo = "CANCELADO"
                        uow.pedido.add(pedido)

            return PagoEstadoResponse(estado=nuevo_estado, pedido_id=pedido_id)


        with PagoUnitOfWork(self._session) as uow:
            pago_local = uow.pago.get_ultimo_by_pedido(pedido_id)
            return PagoEstadoResponse(
                estado=pago_local.mp_status if pago_local else None,
                pedido_id=pedido_id,
            )
