import asyncio
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status
from sqlmodel import Session
from app.core.config import settings
from app.modules.images.model import Imagen
from app.modules.images.schemas import ImagenPublic
from app.modules.images.unit_of_work import ImagenUnitOfWork

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)

ALLOWED_TYPES = {'image/jpg', 'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024

class ImagenService:

    def __init__(self, session: Session):
        self._session = session

    def listar_imagenes(self) -> list[ImagenPublic]:
        with ImagenUnitOfWork(self._session) as uow:
            imagenes = uow.imagen.get_all_ordered()
            return [ImagenPublic.model_validate(imagen) for imagen in imagenes]
        
    def obtener_imagen(self, imagen_id: int) -> ImagenPublic:
        with ImagenUnitOfWork(self._session) as uow:
            imagen = uow.imagen.get_by_id(imagen_id)
            if not imagen:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Imagen no encontrada')
            return ImagenPublic.model_validate(imagen)
        
    async def subir_imagenes(self, archivos: list[UploadFile]) -> list[ImagenPublic]:
        resultados = []
        for archivo in archivos:
            if archivo.content_type not in ALLOWED_TYPES:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Tipo de archivo no permitido: {archivo.content_type}')
            
            contenido = await archivo.read()
            if len(contenido) > MAX_FILE_SIZE:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f'Archivo demasiado grande: {archivo.filename}')
            
            resultado = await asyncio.to_thread(
                cloudinary.uploader.upload,
                contenido,
                folder='foodStore',
                resource_type='image'
            )

            imagen = Imagen(
                public_id=resultado['public_id'],
                url=resultado['secure_url'],
                filename=archivo.filename or resultado['public_id'],
                format=resultado.get('format'),
                width=resultado.get('width'),
                height=resultado.get('height'),
                bytes=resultado.get('bytes')
            )

            with ImagenUnitOfWork(self._session) as uow:
                guardada = uow.imagen.add(imagen)
                resultados.append(ImagenPublic.model_validate(guardada))
        
        return resultados
    
    def eliminar_imagen(self, imagen_id: int) -> None:
        with ImagenUnitOfWork(self._session) as uow:
            imagen = uow.imagen.get_by_id(imagen_id)
            if not imagen:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Imagen no encontrada')
            cloudinary.uploader.destroy(imagen.public_id, resource_type='image')
            uow.imagen.delete(imagen)