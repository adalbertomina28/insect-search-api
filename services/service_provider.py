from services.inaturalist_service import INaturalistService

# Singleton para el servicio de iNaturalist
_inaturalist_service = None

def get_inaturalist_service() -> INaturalistService:
    """
    Obtiene una instancia única del servicio de iNaturalist.
    Esto asegura que la caché se comparta entre todas las solicitudes.
    """
    global _inaturalist_service
    if _inaturalist_service is None:
        _inaturalist_service = INaturalistService()
    return _inaturalist_service
