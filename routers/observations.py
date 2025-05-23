from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
import logging

from models.api_models import (
    Observation, 
    ObservationCreate, 
    ObservationUpdate, 
    ObservationResponse, 
    ObservationsResponse
)
from services.insect_service import InsectService

# Configurar el logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/observations", tags=["observations"])

# Dependency to get the insect service
async def get_insect_service():
    return InsectService()

@router.get("/{observation_id}", response_model=ObservationResponse)
async def get_observation(observation_id: UUID, insect_service: InsectService = Depends(get_insect_service)):
    """Get an observation by ID"""
    result = await insect_service.get_observation(str(observation_id))
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Observation not found")
        )
    
    return {"observation": result["observation"]}

@router.get("/user/{user_id}", response_model=ObservationsResponse)
async def get_user_observations(user_id: UUID, insect_service: InsectService = Depends(get_insect_service)):
    """Get all observations for a user"""
    result = await insect_service.get_user_observations(str(user_id))
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Error getting observations")
        )
    
    # Asegurarnos de que cada observación tenga los campos requeridos
    observations = result["observations"]
    
    # Si no hay observaciones, devolver una respuesta explícita con lista vacía
    # Esto es válido porque ObservationsResponse tiene un valor por defecto para observations
    if len(observations) == 0:
        print(f"User {user_id} has no observations")
    
    return {
        "observations": observations,
        "total": result["total"]
    }

@router.post("/", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
async def create_observation(observation: ObservationCreate, insect_service: InsectService = Depends(get_insect_service)):
    """Create a new observation"""
    result = await insect_service.create_observation(observation.dict())
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Error creating observation")
        )
    
    return {"observation": result["observation"]}

@router.put("/{observation_id}", response_model=ObservationResponse)
async def update_observation(observation_id: UUID, observation: ObservationUpdate, insect_service: InsectService = Depends(get_insect_service)):
    """Update an observation"""
    # Only include non-None values
    update_data = observation.dict(exclude_unset=True)
    
    result = await insect_service.update_observation(str(observation_id), update_data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Observation not found")
        )
    
    return {"observation": result["observation"]}

@router.delete("/{observation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_observation(observation_id: UUID, insect_service: InsectService = Depends(get_insect_service)):
    """Delete an observation"""
    result = await insect_service.delete_observation(str(observation_id))
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Observation not found")
        )
    
    return None
