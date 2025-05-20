import os
import logging
from supabase import create_client, Client
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Configurar logging
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class SupabaseService:
    """Servicio para interactuar con Supabase desde el backend"""
    
    def __init__(self):
        """Inicializa el cliente de Supabase con las credenciales del entorno"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Usamos la service key, no la anon key
        
        if not self.supabase_url or not self.supabase_key:
            logger.error("No se encontraron las credenciales de Supabase en las variables de entorno")
            raise ValueError("SUPABASE_URL y SUPABASE_SERVICE_KEY deben estar configuradas en el archivo .env")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Cliente de Supabase inicializado correctamente")
    
    async def sign_in_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """Inicia sesión con email y contraseña"""
        try:
            response = self.client.auth.sign_in_with_password({"email": email, "password": password})
            return {
                "success": True,
                "session": response.session.json() if response.session else None,
                "user": response.user.json() if response.user else None
            }
        except Exception as e:
            logger.error(f"Error al iniciar sesión con email: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def sign_up_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """Registra un nuevo usuario con email y contraseña"""
        try:
            response = self.client.auth.sign_up({"email": email, "password": password})
            return {
                "success": True,
                "session": response.session.json() if response.session else None,
                "user": response.user.json() if response.user else None
            }
        except Exception as e:
            logger.error(f"Error al registrar usuario: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Envía un correo para restablecer la contraseña"""
        try:
            self.client.auth.reset_password_for_email(email)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error al enviar correo de restablecimiento: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresca el token de autenticación"""
        try:
            response = self.client.auth.refresh_session(refresh_token)
            return {
                "success": True,
                "session": response.session.json() if response.session else None
            }
        except Exception as e:
            logger.error(f"Error al refrescar token: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def sign_out(self, token: str) -> Dict[str, Any]:
        """Cierra la sesión del usuario"""
        try:
            # Configurar el token en el cliente antes de cerrar sesión
            self.client.auth.set_session(token)
            self.client.auth.sign_out()
            return {"success": True}
        except Exception as e:
            logger.error(f"Error al cerrar sesión: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_user_metadata(self, token: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza los metadatos del usuario"""
        try:
            # Configurar el token en el cliente antes de actualizar
            self.client.auth.set_session(token)
            response = self.client.auth.update_user({"data": metadata})
            return {
                "success": True,
                "user": response.user.json() if response.user else None
            }
        except Exception as e:
            logger.error(f"Error al actualizar metadatos: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user(self, token: str) -> Dict[str, Any]:
        """Obtiene la información del usuario actual"""
        try:
            # Configurar el token en el cliente
            self.client.auth.set_session(token)
            user = self.client.auth.get_user()
            return {
                "success": True,
                "user": user.user.json() if user.user else None
            }
        except Exception as e:
            logger.error(f"Error al obtener usuario: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def exchange_code_for_session(self, code: str) -> Dict[str, Any]:
        """Intercambia un código de autenticación por una sesión (para OAuth)"""
        try:
            response = self.client.auth.exchange_code_for_session(code)
            return {
                "success": True,
                "session": response.session.json() if response.session else None,
                "user": response.user.json() if response.user else None
            }
        except Exception as e:
            logger.error(f"Error al intercambiar código: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def sign_in_with_oauth(self, provider: str, redirect_url: str) -> Dict[str, Any]:
        """Inicia el flujo de autenticación OAuth"""
        try:
            response = self.client.auth.sign_in_with_oauth({
                "provider": provider,
                "options": {
                    "redirect_to": redirect_url
                }
            })
            return {
                "success": True,
                "url": response.url
            }
        except Exception as e:
            logger.error(f"Error al iniciar OAuth: {str(e)}")
            return {"success": False, "error": str(e)}
