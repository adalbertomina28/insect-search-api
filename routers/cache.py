from fastapi import APIRouter
from services.service_provider import get_inaturalist_service

router = APIRouter(
    prefix="/api/cache",
    tags=["cache"],
    responses={404: {"description": "No encontrado"}},
)

@router.get("/stats")
async def get_cache_stats():
    """
    Obtiene estadísticas sobre la caché actual
    """
    service = get_inaturalist_service()
    return {
        "total_items": service.cache.get_size(),
        "ttl_seconds": service.cache.ttl_seconds
    }

@router.delete("/clear")
async def clear_cache():
    """
    Limpia toda la caché
    """
    service = get_inaturalist_service()
    service.cache.clear()
    return {"message": "Caché limpiada correctamente"}
