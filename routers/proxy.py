from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import httpx

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
