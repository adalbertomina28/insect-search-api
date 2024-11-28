from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import insects, proxy

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

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Insectos"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
