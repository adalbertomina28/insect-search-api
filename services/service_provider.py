from services.inaturalist_service import INaturalistService
from services.openrouter_service import OpenRouterService

# Singletons para los servicios
_inaturalist_service = None
_openrouter_service = None

# API Key para OpenRouter
OPENROUTER_API_KEY = "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"

def get_inaturalist_service() -> INaturalistService:
    """
    Obtiene una instancia única del servicio de iNaturalist.
    Esto asegura que la caché se comparta entre todas las solicitudes.
    """
    global _inaturalist_service
    if _inaturalist_service is None:
        _inaturalist_service = INaturalistService()
    return _inaturalist_service


def get_openrouter_service() -> OpenRouterService:
    """
    Obtiene una instancia única del servicio de OpenRouter.
    """
    global _openrouter_service
    if _openrouter_service is None:
        _openrouter_service = OpenRouterService(api_key=OPENROUTER_API_KEY)
    return _openrouter_service
