from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from models.api_models import (
    Photo, 
    PhotoCreate, 
    PhotoUpdate, 
    PhotoResponse, 
    PhotosResponse
)
from services.insect_service import InsectService

# Create router
router = APIRouter(prefix="/api/photos", tags=["photos"])

# Dependency to get the insect service
async def get_insect_service():
    return InsectService()

@router.get("/observation/{observation_id}", response_model=PhotosResponse)
async def get_observation_photos(observation_id: UUID, insect_service: InsectService = Depends(get_insect_service)):
    """Get all photos for an observation"""
    result = await insect_service.get_observation_photos(str(observation_id))
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Error getting photos")
        )
    
    return {
        "photos": result["photos"],
        "total": result["total"]
    }

@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def add_photo(photo: PhotoCreate, insect_service: InsectService = Depends(get_insect_service)):
    """Add a photo to an observation"""
    result = await insect_service.add_observation_photo(photo.dict())
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Error adding photo")
        )
    
    return {"photo": result["photo"]}

@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(photo_id: UUID, photo: PhotoUpdate, insect_service: InsectService = Depends(get_insect_service)):
    """Update a photo"""
    # Only include non-None values
    update_data = photo.dict(exclude_unset=True)
    
    result = await insect_service.update_observation_photo(str(photo_id), update_data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Photo not found")
        )
    
    return {"photo": result["photo"]}

@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(photo_id: UUID, insect_service: InsectService = Depends(get_insect_service)):
    """Delete a photo"""
    result = await insect_service.delete_observation_photo(str(photo_id))
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Photo not found")
        )
    
    return None
