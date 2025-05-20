from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging
import os
from services.supabase_service import SupabaseService

# Configurar logging
logger = logging.getLogger(__name__)

# Esquema de seguridad para validar tokens
security = HTTPBearer()

class AuthMiddleware:
    """Middleware para verificar la autenticación de los usuarios"""
    
    def __init__(self):
        """Inicializa el middleware con el servicio de Supabase"""
        self.supabase_service = SupabaseService()
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """
        Verifica que el token JWT sea válido y devuelve la información del usuario
        
        Args:
            credentials: Credenciales de autorización HTTP
            
        Returns:
            Dict: Información del usuario autenticado
            
        Raises:
            HTTPException: Si el token no es válido o ha expirado
        """
        try:
            token = credentials.credentials
            
            # Verificar el token con Supabase
            result = await self.supabase_service.get_user(token)
            
            if not result.get("success", False):
                logger.warning(f"Token inválido: {result.get('error', 'Error desconocido')}")
                raise HTTPException(
                    status_code=401,
                    detail="Token inválido o expirado"
                )
            
            # Devolver la información del usuario
            user_data = result.get("user")
            if not user_data:
                raise HTTPException(
                    status_code=401,
                    detail="No se pudo obtener la información del usuario"
                )
            
            return user_data
        except Exception as e:
            logger.error(f"Error al verificar token: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Error de autenticación"
            )
    
    async def get_current_user(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Obtiene el usuario actual a partir del token de autorización
        
        Args:
            request: Objeto Request de FastAPI
            
        Returns:
            Optional[Dict]: Información del usuario o None si no está autenticado
        """
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.replace("Bearer ", "")
            
            # Verificar el token con Supabase
            result = await self.supabase_service.get_user(token)
            
            if not result.get("success", False):
                return None
            
            # Devolver la información del usuario
            user_data = result.get("user")
            return user_data
        except Exception as e:
            logger.error(f"Error al obtener usuario actual: {str(e)}")
            return None

# Crear una instancia del middleware
auth_middleware = AuthMiddleware()

# Dependencia para verificar la autenticación
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependencia para verificar la autenticación del usuario"""
    return await auth_middleware.verify_token(credentials)

# Dependencia opcional para obtener el usuario actual (si está autenticado)
async def get_optional_user(request: Request):
    """Dependencia opcional para obtener el usuario actual (si está autenticado)"""
    return await auth_middleware.get_current_user(request)
