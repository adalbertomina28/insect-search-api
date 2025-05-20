from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from services.inaturalist_service import INaturalistService
from models.insect import InsectBase, InsectSearchResult, NearbySearchResult
from services.service_provider import get_inaturalist_service
from middleware.auth_middleware import get_current_user

router = APIRouter(
    prefix="/api/insects",
    tags=["insects"],
    responses={404: {"description": "Not found"}},
)

@router.get("/search")
async def search_insects(
    query: str = Query(..., description="Search query for insects"),
    locale: str = Query("es", description="Language code (e.g., 'es' for Spanish, 'en' for English)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=50, description="Results per page"),
) -> InsectSearchResult:
    """
    Search for insects using the iNaturalist API
    """
    service = get_inaturalist_service()
    try:
        data = await service.search_observations(
            query=query,
            locale=locale,
            page=page,
            per_page=per_page
        )
        
        return InsectSearchResult(
            total_results=data.get("total_results", 0),
            page=page,
            per_page=per_page,
            results=[InsectBase(**taxon) for taxon in data.get("results", [])]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nearby")
async def get_nearby_insects(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    locale: str = Query("es", description="Language code (e.g., 'es' for Spanish, 'en' for English)"),
    radius: int = Query(50, ge=1, le=500, description="Search radius in kilometers"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=50, description="Results per page"),
) -> NearbySearchResult:
    """
    Get insects observed near a specific location
    """
    service = get_inaturalist_service()
    try:
        data = await service.get_observations_by_location(
            lat=lat,
            lng=lng,
            locale=locale,
            radius=radius,
            page=page,
            per_page=per_page
        )
        
        return NearbySearchResult(
            total_results=data.get("total_results", 0),
            page=page,
            per_page=per_page,
            results=[InsectBase(**taxon.get("taxon", {})) for taxon in data.get("results", []) if taxon.get("taxon")],
            latitude=lat,
            longitude=lng,
            radius=radius
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{insect_id}")
async def get_insect_details(
    insect_id: int,
    locale: str = Query("es", description="Language code (e.g., 'es' for Spanish, 'en' for English)")
) -> InsectBase:
    """
    Get detailed information about a specific insect
    """
    service = get_inaturalist_service()
    try:
        data = await service.get_species_info(insect_id, locale=locale)
        if not data.get("results"):
            raise HTTPException(status_code=404, detail="Insect not found")
            
        return InsectBase(**data["results"][0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/favorites/list", response_model=List[Dict[str, Any]])
async def get_favorite_insects(
    user_data: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get the list of favorite insects for the authenticated user
    
    This endpoint requires authentication. The user must provide a valid JWT token.
    """
    try:
        # En una implementación real, aquí se consultaría la base de datos
        # para obtener los insectos favoritos del usuario
        # Por ahora, devolvemos una lista de ejemplo
        
        # Obtener el ID del usuario del token
        user_id = user_data.get("id")
        
        # Lista de ejemplo (en una implementación real, se obtendría de la base de datos)
        favorites = [
            {"insect_id": 47219, "name": "Mariposa Monarca", "added_at": "2025-05-18T10:30:00Z"},
            {"insect_id": 47224, "name": "Escarabajo Hércules", "added_at": "2025-05-17T14:20:00Z"},
            {"insect_id": 47157, "name": "Abeja Melífera", "added_at": "2025-05-16T09:15:00Z"}
        ]
        
        return favorites
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener insectos favoritos: {str(e)}")

@router.post("/favorites/add/{insect_id}", response_model=Dict[str, Any])
async def add_favorite_insect(
    insect_id: int,
    user_data: Dict[str, Any] = Depends(get_current_user)
):
    """
    Add an insect to the user's favorites list
    
    This endpoint requires authentication. The user must provide a valid JWT token.
    """
    try:
        # En una implementación real, aquí se agregaría el insecto a la lista de favoritos
        # del usuario en la base de datos
        # Por ahora, devolvemos una respuesta de ejemplo
        
        # Obtener el ID del usuario del token
        user_id = user_data.get("id")
        
        # Verificar primero si el insecto existe
        service = get_inaturalist_service()
        data = await service.get_species_info(insect_id, locale="es")
        if not data.get("results"):
            raise HTTPException(status_code=404, detail="Insecto no encontrado")
        
        insect_name = data["results"][0].get("name", "Insecto desconocido")
        
        return {
            "success": True,
            "message": f"Insecto '{insect_name}' agregado a favoritos",
            "insect_id": insect_id,
            "name": insect_name,
            "added_at": "2025-05-18T21:30:00Z"  # En una implementación real, sería la fecha actual
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar insecto a favoritos: {str(e)}")
