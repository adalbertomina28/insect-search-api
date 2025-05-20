from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr
import logging
from services.supabase_service import SupabaseService

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/api/auth", tags=["auth"])

# Esquema para validar token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modelos de datos para las solicitudes
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UpdateUserMetadataRequest(BaseModel):
    metadata: Dict[str, Any]

class OAuthRequest(BaseModel):
    provider: str
    redirect_url: str

class ExchangeCodeRequest(BaseModel):
    code: str

# Función para obtener el servicio de Supabase
def get_supabase_service():
    return SupabaseService()

# Función para extraer el token de autorización
async def get_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No se proporcionó token de autorización")
    
    # Extraer el token Bearer
    if authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    
    raise HTTPException(status_code=401, detail="Formato de token inválido")

# Endpoints
@router.post("/login")
async def login(request: LoginRequest, supabase: SupabaseService = Depends(get_supabase_service)):
    """Inicia sesión con email y contraseña"""
    result = await supabase.sign_in_with_email(request.email, request.password)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result.get("error", "Error de autenticación"))
    
    return result

@router.post("/signup")
async def signup(request: SignupRequest, supabase: SupabaseService = Depends(get_supabase_service)):
    """Registra un nuevo usuario"""
    result = await supabase.sign_up_with_email(request.email, request.password)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Error al registrar usuario"))
    
    return result

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, supabase: SupabaseService = Depends(get_supabase_service)):
    """Envía un correo para restablecer la contraseña"""
    result = await supabase.reset_password(request.email)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Error al enviar correo de restablecimiento"))
    
    return {"message": "Correo de restablecimiento enviado"}

@router.post("/refresh-token")
async def refresh_token(request: RefreshTokenRequest, supabase: SupabaseService = Depends(get_supabase_service)):
    """Refresca el token de autenticación"""
    result = await supabase.refresh_token(request.refresh_token)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result.get("error", "Error al refrescar token"))
    
    return result

@router.post("/signout")
async def signout(token: str = Depends(get_token), supabase: SupabaseService = Depends(get_supabase_service)):
    """Cierra la sesión del usuario"""
    result = await supabase.sign_out(token)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Error al cerrar sesión"))
    
    return {"message": "Sesión cerrada correctamente"}

@router.post("/update-metadata")
async def update_metadata(
    request: UpdateUserMetadataRequest, 
    token: str = Depends(get_token), 
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Actualiza los metadatos del usuario"""
    result = await supabase.update_user_metadata(token, request.metadata)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Error al actualizar metadatos"))
    
    return result

@router.get("/user")
async def get_user(token: str = Depends(get_token), supabase: SupabaseService = Depends(get_supabase_service)):
    """Obtiene la información del usuario actual"""
    result = await supabase.get_user(token)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result.get("error", "Error al obtener usuario"))
    
    return result

@router.post("/oauth")
async def oauth_login(request: OAuthRequest, supabase: SupabaseService = Depends(get_supabase_service)):
    """Inicia el flujo de autenticación OAuth"""
    result = await supabase.sign_in_with_oauth(request.provider, request.redirect_url)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Error al iniciar OAuth"))
    
    return result

@router.post("/exchange-code")
async def exchange_code(request: ExchangeCodeRequest, supabase: SupabaseService = Depends(get_supabase_service)):
    """Intercambia un código de autenticación por una sesión"""
    result = await supabase.exchange_code_for_session(request.code)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Error al intercambiar código"))
    
    return result
