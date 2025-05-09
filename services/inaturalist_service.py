import httpx
import json
from typing import Dict, Any, Optional
from services.cache_service import CacheService

class INaturalistService:
    def __init__(self, cache_ttl_seconds: int = 86400):  # 24 horas por defecto
        self.base_url = "https://api.inaturalist.org/v1"
        self.headers = {
            "User-Agent": "InsectosApp/1.0",
            "Accept": "application/json"
        }
        self.default_place_id = 7043  # Panama
        self.cache = CacheService(ttl_seconds=cache_ttl_seconds)

    async def search_observations(
        self, 
        query: str, 
        locale: str = "es",
        per_page: int = 10, 
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search for observations in iNaturalist
        Args:
            query: Search term
            locale: Language code (e.g., 'es' for Spanish, 'en' for English)
            per_page: Number of results per page
            page: Page number
        """
        # Crear una clave única para la caché basada en los parámetros de búsqueda
        cache_key = f"search_observations:{query}:{locale}:{per_page}:{page}"
        
        # Verificar si los resultados están en caché
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Si no está en caché, hacer la petición a la API
        async with httpx.AsyncClient() as client:
            params = {
                "q": query,
                "per_page": per_page,
                "page": page,
                "taxon_id": 47158,  # ID for clase Insecta
                "locale": locale,
                "preferred_place_id": self.default_place_id,  # Panama
                "order_by": "observations_count",
                "is_active": "true",
                "rank": "species,subspecies"
            }
            
            response = await client.get(
                f"{self.base_url}/taxa",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            # Guardar el resultado en la caché
            self.cache.set(cache_key, result)
            
            return result

    async def get_species_info(self, taxon_id: int, locale: str = "es") -> Dict[str, Any]:
        """
        Get detailed information about a specific species
        Args:
            taxon_id: The iNaturalist taxon ID
            locale: Language code (e.g., 'es' for Spanish, 'en' for English)
        """
        # Crear una clave única para la caché
        cache_key = f"species_info:{taxon_id}:{locale}"
        
        # Verificar si los resultados están en caché
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
            
        # Si no está en caché, hacer la petición a la API
        async with httpx.AsyncClient() as client:
            params = {
                "locale": locale,
                "preferred_place_id": self.default_place_id,  # Panama
            }
            response = await client.get(
                f"{self.base_url}/taxa/{taxon_id}",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            # Guardar el resultado en la caché
            self.cache.set(cache_key, result)
            
            return result

    async def get_observations_by_location(
        self,
        lat: float,
        lng: float,
        locale: str = "es",
        radius: int = 50,  # km
        per_page: int = 10,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Get observations near a specific location
        Args:
            lat: Latitude
            lng: Longitude
            locale: Language code (e.g., 'es' for Spanish, 'en' for English)
            radius: Search radius in kilometers
            per_page: Number of results per page
            page: Page number
        """
        # Redondear las coordenadas para mejorar las coincidencias de caché
        # (pequeñas variaciones en las coordenadas no deberían generar nuevas consultas)
        rounded_lat = round(lat, 4)  # Aproximadamente 11 metros de precisión
        rounded_lng = round(lng, 4)
        
        # Crear una clave única para la caché
        cache_key = f"observations_location:{rounded_lat}:{rounded_lng}:{locale}:{radius}:{per_page}:{page}"
        
        # Verificar si los resultados están en caché
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
            
        # Si no está en caché, hacer la petición a la API
        async with httpx.AsyncClient() as client:
            params = {
                "lat": lat,
                "lng": lng,
                "radius": radius,
                "per_page": per_page,
                "page": page,
                "taxon_id": 47158,  # ID for clase Insecta
                "locale": locale,
                "preferred_place_id": self.default_place_id,  # Panama
                "order_by": "observed_on",
                "verifiable": "true"
            }
            
            response = await client.get(
                f"{self.base_url}/observations",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            # Guardar el resultado en la caché
            self.cache.set(cache_key, result)
            
            return result
