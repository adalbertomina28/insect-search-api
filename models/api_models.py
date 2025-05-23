from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID, uuid4

# Modelos para catálogos
class CatalogItem(BaseModel):
    """Model for catalog items"""
    id: int
    name: str

class CatalogResponse(BaseModel):
    """Model for catalog response"""
    items: List[CatalogItem]

# Modelos para fotos
class Photo(BaseModel):
    """Model for observation photos"""
    id: Optional[UUID] = Field(default_factory=uuid4)
    observation_id: UUID
    photo_url: str
    description: Optional[str] = None
    order: Optional[int] = None
    created_at: Optional[datetime] = None

class PhotoCreate(BaseModel):
    """Model for creating observation photos"""
    observation_id: UUID
    photo_url: str
    description: Optional[str] = None
    order: Optional[int] = None

class PhotoUpdate(BaseModel):
    """Model for updating observation photos"""
    photo_url: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None

# Modelos para observaciones
class Observation(BaseModel):
    """Model for insect observations"""
    id: Optional[UUID] = Field(default_factory=uuid4)
    user_id: UUID
    inaturalist_id: int
    scientific_name: str
    common_name: str
    observation_date: date
    latitude: float
    longitude: float
    condition_id: int
    state_id: int
    stage_id: int
    sex_id: int
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    photos: Optional[List[Photo]] = []

class PhotoCreateNested(BaseModel):
    """Model for creating photos nested within an observation"""
    photo_url: str
    description: Optional[str] = None
    order: Optional[int] = None

class ObservationCreate(BaseModel):
    """Model for creating insect observations"""
    user_id: UUID
    inaturalist_id: int
    scientific_name: str
    common_name: str
    observation_date: date
    latitude: float
    longitude: float
    condition_id: int
    state_id: int
    stage_id: int
    sex_id: int
    description: Optional[str] = None
    photos: Optional[List[PhotoCreateNested]] = []

class ObservationUpdate(BaseModel):
    """Model for updating insect observations"""
    inaturalist_id: Optional[int] = None
    scientific_name: Optional[str] = None
    common_name: Optional[str] = None
    observation_date: Optional[date] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    condition_id: Optional[int] = None
    state_id: Optional[int] = None
    stage_id: Optional[int] = None
    sex_id: Optional[int] = None
    description: Optional[str] = None

# Modelos para respuestas
class ObservationResponse(BaseModel):
    """Model for observation response"""
    observation: Observation

class ObservationsResponse(BaseModel):
    """Model for multiple observations response"""
    observations: List[Observation] = []
    total: int

class PhotoResponse(BaseModel):
    """Model for photo response"""
    photo: Photo

class PhotosResponse(BaseModel):
    """Model for multiple photos response"""
    photos: List[Photo]
    total: int
