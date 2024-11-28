from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TaxonPhoto(BaseModel):
    id: Optional[int] = None
    attribution: Optional[str] = None
    license_code: Optional[str] = None
    url: Optional[str] = None
    medium_url: Optional[str] = None
    square_url: Optional[str] = None

class ConservationStatus(BaseModel):
    status: Optional[str] = None
    status_name: Optional[str] = None
    iucn: Optional[int] = None
    description: Optional[str] = None

class Ancestor(BaseModel):
    id: int
    name: str
    rank: Optional[str] = None
    rank_level: Optional[int] = None
    preferred_common_name: Optional[str] = None

class InsectBase(BaseModel):
    id: int
    name: str
    preferred_common_name: Optional[str] = None
    matched_term: Optional[str] = None
    iconic_taxon_name: Optional[str] = None
    rank: Optional[str] = None
    rank_level: Optional[int] = None
    ancestor_ids: Optional[List[int]] = None
    ancestors: Optional[List[Ancestor]] = None
    default_photo: Optional[Dict[str, Any]] = None
    taxon_photos: Optional[List[Dict[str, Any]]] = None
    conservation_status: Optional[ConservationStatus] = None
    wikipedia_url: Optional[str] = None
    wikipedia_summary: Optional[str] = None
    observations_count: Optional[int] = None
    complete_species_count: Optional[int] = None
    native: Optional[bool] = None
    introduced: Optional[bool] = None
    threatened: Optional[bool] = None
    endemic: Optional[bool] = None
    extinct: Optional[bool] = None
    colors: Optional[List[Dict[str, Any]]] = None

class InsectSearchResult(BaseModel):
    total_results: int
    page: int
    per_page: int
    results: List[InsectBase]

class NearbySearchResult(BaseModel):
    total_results: int
    page: int
    per_page: int
    results: List[InsectBase]
    latitude: float
    longitude: float
    radius: int
