from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import insects, proxy, identification, cache, chatbot
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Insectos API",
    description="API para la aplicación de insectos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(insects.router)
app.include_router(proxy.router)
app.include_router(identification.router)
app.include_router(cache.router)
app.include_router(chatbot.router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Insectos"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
