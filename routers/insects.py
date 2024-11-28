from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.inaturalist_service import INaturalistService
from models.insect import InsectBase, InsectSearchResult, NearbySearchResult

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
    service = INaturalistService()
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

@router.get("/{insect_id}")
async def get_insect_details(
    insect_id: int,
    locale: str = Query("es", description="Language code (e.g., 'es' for Spanish, 'en' for English)")
) -> InsectBase:
    """
    Get detailed information about a specific insect
    """
    service = INaturalistService()
    try:
        data = await service.get_species_info(insect_id, locale=locale)
        if not data.get("results"):
            raise HTTPException(status_code=404, detail="Insect not found")
            
        return InsectBase(**data["results"][0])
    except HTTPException:
        raise
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
    service = INaturalistService()
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
