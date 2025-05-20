from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from services.minio_service import minio_service
import logging
from typing import Optional

router = APIRouter(
    prefix="/storage",
    tags=["storage"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    path: str = Form(None)
):
    """
    Sube una imagen a MinIO y devuelve la URL.
    
    Args:
        file: El archivo a subir (debe ser una imagen)
        path: Ruta opcional dentro del bucket donde guardar la imagen (se creará si no existe)
        
    Returns:
        dict: Diccionario con la URL de la imagen y otros metadatos
    """
    try:
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser una imagen (JPEG, PNG, etc.)"
            )
        
        # Mostrar información de depuración
        logger.info(f"Subiendo imagen con path: {path}")
        
        # Subir imagen a MinIO
        result = await minio_service.upload_image(file, path=path)
        
        # Mostrar información detallada del resultado
        logger.info(f"Resultado de la subida: {result}")
        
        return {
            "success": True,
            "message": "Imagen subida exitosamente",
            "image_url": result["image_url"],
            "object_name": result["object_name"],
            "content_type": result["content_type"]
        }
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al subir imagen: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la imagen: {str(e)}"
        )
