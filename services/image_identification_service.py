import httpx
import base64
from typing import Dict, Any, List, Optional
import os
import logging

logger = logging.getLogger(__name__)

class ImageIdentificationService:
    def __init__(self):
        self.base_url = "https://api.inaturalist.org/v1"
        
        # Obtener el API token del entorno o usar uno por defecto
        self.api_token = os.environ.get("INATURALIST_API_TOKEN", "")
        
        self.headers = {
            "User-Agent": "InsectosApp/1.0",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_token}" if self.api_token else ""
        }
        
        # Si no hay token, usar el método alternativo con JWT
        if not self.api_token:
            self.jwt_token = os.environ.get("INATURALIST_JWT_TOKEN", "")
            if self.jwt_token:
                self.headers["Authorization"] = f"JWT {self.jwt_token}"
        
        self.default_place_id = 7043  # Panama
        
        # Modo de demostración para desarrollo
        self.demo_mode = os.environ.get("DEMO_MODE", "false").lower() == "true"
        
        logger.info(f"Inicializando servicio de identificación de imágenes")
        if not self.api_token and not os.environ.get("INATURALIST_JWT_TOKEN"):
            if self.demo_mode:
                logger.info("Ejecutando en modo de demostración con datos simulados")
            else:
                logger.warning("No se encontró token de API o JWT para iNaturalist. Las solicitudes pueden fallar.")
        
    async def identify_image(self, image_data: bytes, latitude: Optional[float] = None, 
                           longitude: Optional[float] = None, locale: str = "es") -> Dict[str, Any]:
        # Si estamos en modo de demostración, devolver datos simulados
        if self.demo_mode:
            return self._get_demo_results(locale)
        """
        Identifica insectos en una imagen utilizando la API de visión por computadora de iNaturalist
        
        Args:
            image_data: Datos binarios de la imagen
            latitude: Latitud opcional para mejorar la precisión
            longitude: Longitud opcional para mejorar la precisión
            locale: Código de idioma (ej. 'es' para español, 'en' para inglés)
            
        Returns:
            Resultados de la identificación con probabilidades
        """
        try:
            # Codificar la imagen en base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Preparar los datos para la solicitud
            payload = {
                "image": image_base64,
                "locale": locale,
                "preferred_place_id": self.default_place_id
            }
            
            # Añadir coordenadas si están disponibles
            if latitude is not None and longitude is not None:
                payload["latitude"] = latitude
                payload["longitude"] = longitude
                
            # Añadir filtro para clase Insecta
            payload["taxon_id"] = 47158  # ID para clase Insecta
            
            # Realizar la solicitud a la API de iNaturalist
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Nota: Esta URL puede cambiar ya que no es una API pública oficial
                api_url = f"{self.base_url}/computervision/score_image"
                
                # Imprimir información de depuración (sin tokens sensibles)
                debug_headers = self.headers.copy()
                if "Authorization" in debug_headers:
                    debug_headers["Authorization"] = "[REDACTED]"
                    
                logger.info(f"Enviando solicitud a: {api_url}")
                logger.debug(f"Headers: {debug_headers}")
                
                response = await client.post(
                    api_url,
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Filtrar solo resultados de insectos
                    if "results" in result:
                        # Ordenar por probabilidad descendente
                        sorted_results = sorted(
                            result["results"], 
                            key=lambda x: x.get("score", 0), 
                            reverse=True
                        )
                        return {
                            "results": sorted_results[:10],  # Devolver los 10 mejores resultados
                            "status": "success"
                        }
                    return {
                        "results": [],
                        "status": "success",
                        "message": "No se encontraron insectos en la imagen"
                    }
                else:
                    error_msg = f"Error en la API de iNaturalist: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    
                    # Mensajes específicos según el código de error
                    if response.status_code == 401:
                        return {
                            "status": "error",
                            "message": "Error de autenticación con la API de iNaturalist. Verifica las credenciales.",
                            "details": response.text
                        }
                    elif response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "No tienes permiso para acceder a este recurso de iNaturalist.",
                            "details": response.text
                        }
                    elif response.status_code == 429:
                        return {
                            "status": "error",
                            "message": "Has excedido el límite de solicitudes a la API de iNaturalist.",
                            "details": response.text
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"Error en la API de iNaturalist: {response.status_code}",
                            "details": response.text
                        }
                    
        except Exception as e:
            logger.exception(f"Error al identificar la imagen: {str(e)}")
            return {
                "status": "error",
                "message": f"Error al procesar la imagen: {str(e)}"
            }
            
    def _get_demo_results(self, locale: str = "es") -> Dict[str, Any]:
        """Devuelve resultados simulados para el modo de demostración"""
        # Datos simulados de insectos comunes en Panamá
        demo_results = [
            {
                "taxon": {
                    "id": 47224,
                    "name": "Danaus plexippus",
                    "preferred_common_name": "Mariposa monarca" if locale == "es" else "Monarch Butterfly",
                    "rank": "species",
                    "default_photo": {
                        "medium_url": "https://inaturalist-open-data.s3.amazonaws.com/photos/58912610/medium.jpeg"
                    }
                },
                "score": 0.95
            },
            {
                "taxon": {
                    "id": 47219,
                    "name": "Papilio cresphontes",
                    "preferred_common_name": "Mariposa cometa gigante" if locale == "es" else "Giant Swallowtail",
                    "rank": "species",
                    "default_photo": {
                        "medium_url": "https://inaturalist-open-data.s3.amazonaws.com/photos/59543912/medium.jpeg"
                    }
                },
                "score": 0.85
            },
            {
                "taxon": {
                    "id": 47858,
                    "name": "Atta cephalotes",
                    "preferred_common_name": "Hormiga cortadora de hojas" if locale == "es" else "Leafcutter Ant",
                    "rank": "species",
                    "default_photo": {
                        "medium_url": "https://inaturalist-open-data.s3.amazonaws.com/photos/59287185/medium.jpeg"
                    }
                },
                "score": 0.78
            },
            {
                "taxon": {
                    "id": 48527,
                    "name": "Morpho helenor",
                    "preferred_common_name": "Morfo azul" if locale == "es" else "Blue Morpho",
                    "rank": "species",
                    "default_photo": {
                        "medium_url": "https://inaturalist-open-data.s3.amazonaws.com/photos/58721351/medium.jpeg"
                    }
                },
                "score": 0.72
            },
            {
                "taxon": {
                    "id": 48721,
                    "name": "Periplaneta americana",
                    "preferred_common_name": "Cucaracha americana" if locale == "es" else "American Cockroach",
                    "rank": "species",
                    "default_photo": {
                        "medium_url": "https://inaturalist-open-data.s3.amazonaws.com/photos/58982145/medium.jpeg"
                    }
                },
                "score": 0.65
            }
        ]
        
        return {
            "results": demo_results,
            "status": "success",
            "message": "Resultados de demostración (modo sin conexión)"
        }
