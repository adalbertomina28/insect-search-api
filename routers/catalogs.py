from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from models.api_models import CatalogResponse
from services.insect_service import InsectService

# Create router
router = APIRouter(prefix="/api/catalogs", tags=["catalogs"])

# Dependency to get the insect service
async def get_insect_service():
    return InsectService()

@router.get("/conditions", response_model=CatalogResponse)
async def get_conditions_catalog(insect_service: InsectService = Depends(get_insect_service)):
    """Get catalog of observation conditions (captivity/wild)"""
    result = await insect_service.get_catalog("conditions")
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Error getting catalog")
        )
    
    return {"items": result["items"]}

@router.get("/states", response_model=CatalogResponse)
async def get_states_catalog(insect_service: InsectService = Depends(get_insect_service)):
    """Get catalog of insect states (alive/dead/unknown)"""
    result = await insect_service.get_catalog("states")
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Error getting catalog")
        )
    
    return {"items": result["items"]}

@router.get("/stages", response_model=CatalogResponse)
async def get_stages_catalog(insect_service: InsectService = Depends(get_insect_service)):
    """Get catalog of insect life stages (egg/juvenile/adult/unknown)"""
    result = await insect_service.get_catalog("stages")
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Error getting catalog")
        )
    
    return {"items": result["items"]}

@router.get("/sexes", response_model=CatalogResponse)
async def get_sexes_catalog(insect_service: InsectService = Depends(get_insect_service)):
    """Get catalog of insect sexes (male/female/undetermined)"""
    result = await insect_service.get_catalog("sexes")
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Error getting catalog")
        )
    
    return {"items": result["items"]}
