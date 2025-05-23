import os
import logging
from supabase import create_client, Client
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from uuid import UUID
from postgis import Point

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsectService:
    """Service for interacting with the insect observation database"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be defined in environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase client initialized")
    
    def _convert_to_db_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert API field names to database field names"""
        field_mapping = {
            # Observation fields
            "user_id": "user_id",
            "inaturalist_id": "inaturalist_id",
            "scientific_name": "nombre_cientifico",
            "common_name": "nombre_comun",
            "observation_date": "fecha_observacion",
            "latitude": None,  # Will be handled separately for PostGIS
            "longitude": None,  # Will be handled separately for PostGIS
            "condition_id": "condicion_id",
            "state_id": "estado_id",
            "stage_id": "etapa_id",
            "sex_id": "sexo_id",
            "description": "descripcion",
            # Photo fields
            "photo_url": "url_foto",
            "order": "orden",
            "observation_id": "observacion_id"
        }
        
        result = {}
        for key, value in data.items():
            if key in field_mapping and field_mapping[key] is not None:
                result[field_mapping[key]] = value
            elif key not in field_mapping:
                # Keep fields that aren't in our mapping (like id)
                result[key] = value
        
        # Handle location separately
        if "latitude" in data and "longitude" in data:
            try:
                lat = float(data["latitude"])
                lng = float(data["longitude"])
                # Crear punto geográfico en formato WKT para PostGIS
                result["ubicacion"] = f"POINT({lng} {lat})"
                logger.info(f"Created PostGIS point: {result['ubicacion']}")
            except (ValueError, TypeError) as e:
                logger.error(f"Error converting coordinates to PostGIS format: {e}")
                # No incluir ubicación si hay error en las coordenadas
        
        return result
    
    def _convert_from_db_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert database field names to API field names"""
        field_mapping = {
            # Observation fields
            "user_id": "user_id",
            "inaturalist_id": "inaturalist_id",
            "nombre_cientifico": "scientific_name",
            "nombre_comun": "common_name",
            "fecha_observacion": "observation_date",
            "ubicacion": None,  # Will be handled separately for PostGIS
            "condicion_id": "condition_id",
            "estado_id": "state_id",
            "etapa_id": "stage_id",
            "sexo_id": "sex_id",
            "descripcion": "description",
            "created_at": "created_at",
            # Photo fields
            "url_foto": "photo_url",
            "orden": "order",
            "observacion_id": "observation_id"
        }
        
        result = {}
        for key, value in data.items():
            if key in field_mapping and field_mapping[key] is not None:
                result[field_mapping[key]] = value
            elif key not in field_mapping:
                # Keep fields that aren't in our mapping (like id)
                result[key] = value
        
        # Handle location separately
        if "ubicacion" in data and data["ubicacion"]:
            try:
                point_str = data["ubicacion"]
                # Manejar diferentes formatos posibles de PostGIS
                if isinstance(point_str, str):
                    # Formato WKT: POINT(lng lat)
                    coords = point_str.replace("POINT(", "").replace(")", "").split()
                    if len(coords) == 2:
                        result["longitude"] = float(coords[0])
                        result["latitude"] = float(coords[1])
                elif hasattr(point_str, 'x') and hasattr(point_str, 'y'):
                    # Objeto Point de PostGIS
                    result["longitude"] = float(point_str.x)
                    result["latitude"] = float(point_str.y)
                elif isinstance(point_str, dict) and 'coordinates' in point_str:
                    # Formato GeoJSON
                    coords = point_str['coordinates']
                    if len(coords) == 2:
                        result["longitude"] = float(coords[0])
                        result["latitude"] = float(coords[1])
            except Exception as e:
                logger.error(f"Error processing location: {e}")
                # Asegurar que siempre tengamos valores por defecto para evitar errores de validación
                result["longitude"] = 0.0
                result["latitude"] = 0.0
        
        return result
    
    def _serialize_uuid_and_date(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert UUIDs and dates to strings for JSON serialization"""
        result = {}
        for key, value in data.items():
            if isinstance(value, UUID):
                result[key] = str(value)
            elif isinstance(value, (date, datetime)):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = self._serialize_uuid_and_date(value)
            elif isinstance(value, list):
                result[key] = [
                    self._serialize_uuid_and_date(item) if isinstance(item, dict) 
                    else str(item) if isinstance(item, UUID)
                    else item.isoformat() if isinstance(item, (date, datetime))
                    else item 
                    for item in value
                ]
            else:
                result[key] = value
        return result
    
    # Catalog operations
    
    async def get_catalog(self, catalog_name: str) -> Dict[str, Any]:
        """Get catalog values"""
        catalog_mapping = {
            "conditions": "condicion_observacion",
            "states": "estado_insecto",
            "stages": "etapa_insecto",
            "sexes": "sexo_insecto"
        }
        
        db_table = catalog_mapping.get(catalog_name)
        if not db_table:
            return {"success": False, "error": f"Unknown catalog: {catalog_name}"}
        
        try:
            response = self.client.table(db_table).select("id, nombre as name").execute()
            
            if response.data:
                return {"success": True, "items": response.data}
            else:
                return {"success": True, "items": []}
        except Exception as e:
            logger.error(f"Error getting catalog {catalog_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Observation operations
    
    async def get_observation(self, observation_id: str) -> Dict[str, Any]:
        """Get an observation by ID"""
        try:
            response = self.client.table("observaciones").select("*, observacion_fotos(*)").eq("id", observation_id).execute()
            
            if not response.data:
                return {"success": False, "error": "Observation not found"}
            
            # Log the raw data for debugging
            logger.info(f"Raw observation data: {response.data[0]}")
            
            # Convert to API format
            observation_data = self._convert_from_db_format(response.data[0])
            
            # Ensure latitude and longitude are included
            if "ubicacion" in response.data[0] and response.data[0]["ubicacion"]:
                try:
                    point_str = response.data[0]["ubicacion"]
                    if isinstance(point_str, str):
                        coords = point_str.replace("POINT(", "").replace(")", "").split()
                        if len(coords) == 2:
                            observation_data["longitude"] = float(coords[0])
                            observation_data["latitude"] = float(coords[1])
                except Exception as e:
                    logger.error(f"Error extracting coordinates: {e}")
            
            # If coordinates are still missing, add default values
            if "latitude" not in observation_data or "longitude" not in observation_data:
                observation_data["latitude"] = 0.0
                observation_data["longitude"] = 0.0
                logger.warning("Using default coordinates (0,0) for observation")
            
            # Process photos if they exist
            if "observacion_fotos" in response.data[0] and response.data[0]["observacion_fotos"]:
                photos = []
                for photo in response.data[0]["observacion_fotos"]:
                    photos.append(self._convert_from_db_format(photo))
                observation_data["photos"] = photos
            else:
                observation_data["photos"] = []
            
            # Log the final observation data for debugging
            logger.info(f"Final observation data: {observation_data}")
            
            return {"success": True, "observation": observation_data}
        except Exception as e:
            logger.error(f"Error getting observation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_observations(self, user_id: str) -> Dict[str, Any]:
        """Get all observations for a user"""
        try:
            response = self.client.table("observaciones").select("*, observacion_fotos(*)").eq("user_id", user_id).execute()
            
            observations = []
            for obs in response.data:
                observation_data = self._convert_from_db_format(obs)
                
                # Process photos if they exist
                if "observacion_fotos" in obs and obs["observacion_fotos"]:
                    photos = []
                    for photo in obs["observacion_fotos"]:
                        photos.append(self._convert_from_db_format(photo))
                    observation_data["photos"] = photos
                else:
                    observation_data["photos"] = []
                
                # Asegurarse de que latitude y longitude estén presentes
                if "latitude" not in observation_data or observation_data["latitude"] is None:
                    observation_data["latitude"] = 0.0
                    logger.warning(f"Observation {obs.get('id', 'unknown')} missing latitude, using default value")
                
                if "longitude" not in observation_data or observation_data["longitude"] is None:
                    observation_data["longitude"] = 0.0
                    logger.warning(f"Observation {obs.get('id', 'unknown')} missing longitude, using default value")
                
                observations.append(observation_data)
            
            # Log para depuración
            logger.info(f"Found {len(observations)} observations for user {user_id}")
            
            return {"success": True, "observations": observations, "total": len(observations)}
        except Exception as e:
            logger.error(f"Error getting user observations: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_observation(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new observation with photos in a single transaction"""
        try:
            # Extract photos if present
            photos = observation_data.pop("photos", [])
            
            # Save original coordinates for later use
            original_latitude = observation_data.get("latitude")
            original_longitude = observation_data.get("longitude")
            
            # Log original data for debugging
            logger.info(f"Original observation data: {observation_data}")
            
            # Convert UUIDs and dates to strings
            observation_data = self._serialize_uuid_and_date(observation_data)
            
            # Convert to database format
            db_data = self._convert_to_db_format(observation_data)
            
            # Create the observation
            logger.info(f"Observation data to insert: {db_data}")
            response = self.client.table("observaciones").insert(db_data).execute()
            
            if not response.data:
                return {"success": False, "error": "Error creating observation"}
            
            # Get the created observation ID
            observation_id = response.data[0]["id"]
            
            # Add photos if any
            created_photos = []
            if photos:
                for i, photo in enumerate(photos):
                    # Add observation ID and order if not specified
                    photo_data = dict(photo)
                    photo_data["observacion_id"] = observation_id  # Usar observacion_id en lugar de observation_id
                    if "order" not in photo_data or photo_data["order"] is None:
                        photo_data["orden"] = i + 1  # Usar orden en lugar de order
                    elif "order" in photo_data:
                        # Renombrar order a orden
                        photo_data["orden"] = photo_data.pop("order")
                    
                    # Add the photo
                    photo_result = await self.add_observation_photo(photo_data)
                    if photo_result["success"]:
                        created_photos.append(photo_result["photo"])
                    else:
                        logger.warning(f"Failed to add photo: {photo_result.get('error')}")
            
            # Get the complete observation with the correct format
            observation_result = await self.get_observation(observation_id)
            
            if observation_result["success"]:
                created_observation = observation_result["observation"]
                created_observation["photos"] = created_photos
                
                # Ensure latitude and longitude are included
                if ("latitude" not in created_observation or "longitude" not in created_observation) and original_latitude is not None and original_longitude is not None:
                    created_observation["latitude"] = float(original_latitude)
                    created_observation["longitude"] = float(original_longitude)
                    logger.info(f"Added original coordinates: {original_latitude}, {original_longitude}")
                
                return {"success": True, "observation": created_observation}
            else:
                # Fallback to basic conversion if get_observation fails
                created_observation = self._convert_from_db_format(response.data[0])
                created_observation["photos"] = created_photos
                
                # Ensure latitude and longitude are included
                if "latitude" not in created_observation or "longitude" not in created_observation:
                    if original_latitude is not None and original_longitude is not None:
                        created_observation["latitude"] = float(original_latitude)
                        created_observation["longitude"] = float(original_longitude)
                    else:
                        created_observation["latitude"] = 0.0
                        created_observation["longitude"] = 0.0
                        logger.warning("Using default coordinates (0,0) for observation")
                
                return {"success": True, "observation": created_observation}
        except Exception as e:
            logger.error(f"Error creating observation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_observation(self, observation_id: str, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an observation"""
        try:
            # Convert UUIDs and dates to strings
            observation_data = self._serialize_uuid_and_date(observation_data)
            
            # Convert to database format
            db_data = self._convert_to_db_format(observation_data)
            
            # Update the observation
            logger.info(f"Observation data to update: {db_data}")
            response = self.client.table("observaciones").update(db_data).eq("id", observation_id).execute()
            
            if not response.data:
                return {"success": False, "error": "Observation not found"}
            
            # Get the complete updated observation with photos
            return await self.get_observation(observation_id)
        except Exception as e:
            logger.error(f"Error updating observation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def delete_observation(self, observation_id: str) -> Dict[str, Any]:
        """Delete an observation"""
        try:
            # First delete associated photos
            self.client.table("observacion_fotos").delete().eq("observacion_id", observation_id).execute()
            
            # Then delete the observation
            response = self.client.table("observaciones").delete().eq("id", observation_id).execute()
            
            if not response.data:
                return {"success": False, "error": "Observation not found"}
            
            return {"success": True, "message": "Observation deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting observation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Photo operations
    
    async def add_observation_photo(self, photo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a photo to an observation"""
        try:
            # Convert UUIDs to strings
            photo_data = self._serialize_uuid_and_date(photo_data)
            
            # Rename observation_id to observacion_id if present
            if "observation_id" in photo_data:
                photo_data["observacion_id"] = photo_data.pop("observation_id")
                
            # Rename order to orden if present
            if "order" in photo_data:
                photo_data["orden"] = photo_data.pop("order")
            
            # Log the photo data for debugging
            logger.info(f"Photo data before conversion: {photo_data}")
            
            # Asegurarse de que el campo photo_url se mapee correctamente a url_foto
            if "photo_url" in photo_data:
                photo_data["url_foto"] = photo_data.pop("photo_url")
            
            # Convert to database format
            db_data = self._convert_to_db_format(photo_data)
            
            # Log the database data for debugging
            logger.info(f"Photo data to insert: {db_data}")
            
            # Add the photo
            response = self.client.table("observacion_fotos").insert(db_data).execute()
            
            if not response.data:
                return {"success": False, "error": "Error adding photo"}
            
            # Convert back to API format
            created_photo = self._convert_from_db_format(response.data[0])
            
            return {"success": True, "photo": created_photo}
        except Exception as e:
            logger.error(f"Error adding photo: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_observation_photo(self, photo_id: str, photo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a photo"""
        try:
            # Convert to database format
            db_data = self._convert_to_db_format(photo_data)
            
            # Update the photo
            response = self.client.table("observacion_fotos").update(db_data).eq("id", photo_id).execute()
            
            if not response.data:
                return {"success": False, "error": "Photo not found"}
            
            # Convert back to API format
            updated_photo = self._convert_from_db_format(response.data[0])
            
            return {"success": True, "photo": updated_photo}
        except Exception as e:
            logger.error(f"Error updating photo: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def delete_observation_photo(self, photo_id: str) -> Dict[str, Any]:
        """Delete a photo"""
        try:
            response = self.client.table("observacion_fotos").delete().eq("id", photo_id).execute()
            
            if not response.data:
                return {"success": False, "error": "Photo not found"}
            
            return {"success": True, "message": "Photo deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting photo: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_observation_photos(self, observation_id: str) -> Dict[str, Any]:
        """Get all photos for an observation"""
        try:
            response = self.client.table("observacion_fotos").select("*").eq("observacion_id", observation_id).order("orden").execute()
            
            photos = []
            for photo in response.data:
                photos.append(self._convert_from_db_format(photo))
            
            return {"success": True, "photos": photos, "total": len(photos)}
        except Exception as e:
            logger.error(f"Error getting observation photos: {str(e)}")
            return {"success": False, "error": str(e)}
