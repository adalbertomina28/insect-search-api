from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import Optional
from services.image_identification_service import ImageIdentificationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/identification",
    tags=["identification"],
    responses={404: {"description": "Not found"}},
)

@router.post("/identify")
async def identify_insect(
    image: UploadFile = File(..., description="Imagen del insecto a identificar"),
    latitude: Optional[float] = Form(None, description="Latitud opcional para mejorar la precisión"),
    longitude: Optional[float] = Form(None, description="Longitud opcional para mejorar la precisión"),
    locale: str = Form("es", description="Código de idioma (ej. 'es' para español, 'en' para inglés)")
):
    """
    Identifica insectos en una imagen utilizando la API de visión por computadora de iNaturalist
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    try:
        # Leer los datos de la imagen
        image_data = await image.read()
        
        # Validar tamaño de la imagen (máximo 10MB)
        if len(image_data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="La imagen es demasiado grande (máximo 10MB)")
        
        # Procesar la imagen con el servicio de identificación
        service = ImageIdentificationService()
        result = await service.identify_image(
            image_data=image_data,
            latitude=latitude,
            longitude=longitude,
            locale=locale
        )
        
        if result.get("status") == "error":
            logger.error(f"Error en la identificación: {result.get('message')}")
            raise HTTPException(status_code=500, detail=result.get("message", "Error en la identificación"))
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
