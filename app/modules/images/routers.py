from fastapi import APIRouter, Depends, UploadFile, File
from sqlmodel import Session

from app.core.database import get_session
from app.modules.images.schemas import ImagenPublic
from app.modules.images.service import ImagenService

router = APIRouter()
def get_image_service(session: Session = Depends(get_session)) -> ImagenService:
    return ImagenService(session)

@router.get("/", response_model=list[ImagenPublic])
def listar_imagenes(svc: ImagenService = Depends(get_image_service)):
    return svc.listar_imagenes()

@router.get("/{imagen_id}", response_model=ImagenPublic)
def obtener_imagen(imagen_id: int, svc: ImagenService = Depends(get_image_service)):
    return svc.obtener_imagen(imagen_id)

@router.post("/imagen", response_model=list[ImagenPublic])
async def subir_imagenes(files: list[UploadFile] = File(...), svc: ImagenService = Depends(get_image_service)):
    resultado = await svc.subir_imagenes(files)
    return resultado

@router.delete("/imagen/{imagen_id}", status_code=204)
def eliminar_imagen(imagen_id: int, svc: ImagenService = Depends(get_image_service)):
    svc.eliminar_imagen(imagen_id)

