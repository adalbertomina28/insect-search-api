from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import re
from services.minio_service import minio_service

router = APIRouter(
    prefix="/api/proxy",
    tags=["proxy"],
    responses={404: {"description": "Not found"}},
)

@router.get("/image")
async def proxy_image(url: str = Query(..., description="URL of the image to proxy")):
    """
    Proxy an image from another domain
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                return StreamingResponse(
                    content=response.iter_bytes(),
                    media_type=response.headers.get("content-type", "image/jpeg"),
                    headers={
                        "Cache-Control": "public, max-age=31536000",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch image")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signed-url")
async def get_signed_url(object_url: str = Query(..., description="URL completa del objeto en Minio"), expires: int = Query(3600, description="Tiempo de expiración en segundos")):
    """
    Genera una URL firmada temporal para acceder a un objeto en Minio
    
    Args:
        object_url: URL completa del objeto en Minio
        expires: Tiempo de expiración en segundos (por defecto: 1 hora)
    
    Returns:
        JSONResponse con la URL firmada
    """
    try:
        # Extraer el nombre del objeto de la URL
        # Ejemplo: http://31.97.11.223:9000/insect-observations/user_id_here/0fe52bd8-8c15-4b98-88fb-25c4c587a691.jpg
        # -> insect-observations/user_id_here/0fe52bd8-8c15-4b98-88fb-25c4c587a691.jpg
        
        # Patrón para extraer el bucket y el objeto
        pattern = r'https?://[^/]+/([^/]+)/(.+)'
        match = re.match(pattern, object_url)
        
        if not match:
            raise HTTPException(status_code=400, detail="URL de objeto inválida")
        
        bucket_name = match.group(1)
        object_name = match.group(2)
        
        # Verificar que el bucket coincide con el configurado en el servicio
        if bucket_name != minio_service.bucket_name:
            # Si no coincide, incluir el bucket en el nombre del objeto
            object_name = f"{bucket_name}/{object_name}"
        
        # Generar URL firmada
        signed_url = minio_service.generate_presigned_url(object_name, expires)
        
        if not signed_url:
            raise HTTPException(status_code=404, detail="Objeto no encontrado")
        
        return JSONResponse({
            "signed_url": signed_url,
            "expires_in": expires,
            "original_url": object_url
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
