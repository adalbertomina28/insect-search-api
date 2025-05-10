import os
from services.inaturalist_service import INaturalistService
from services.openrouter_service import OpenRouterService

# Singletons para los servicios
_inaturalist_service = None
_openrouter_service = None

# Obtener API Key para OpenRouter desde variable de entorno o usar valor por defecto
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")

# Limpiar la API key para evitar problemas con espacios o saltos de línea
OPENROUTER_API_KEY = OPENROUTER_API_KEY.strip() if OPENROUTER_API_KEY else ""

# Verificar si estamos usando la API key de entorno o la predeterminada
if os.environ.get("OPENROUTER_API_KEY"):
    print("INFO: Usando API key de OpenRouter desde variable de entorno")
else:
    print("INFO: Usando API key de OpenRouter predeterminada para desarrollo local")

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
