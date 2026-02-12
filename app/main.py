from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.core.database import init_db
from app.api import auth, planetas

# --- NUEVA IMPORTACIÓN PARA MONITOREO ---
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manejador del ciclo de vida de la aplicación.
    """
    print("🚀 Iniciando aplicación y base de datos...")
    # Podrías llamar a init_db() aquí si es necesario
    yield
    print("👋 Apagando aplicación...")

app = FastAPI(
    title="Sistema de Gestión de Planetas",
    description="API REST para la gestión de planetas con monitoreo integrado.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CONFIGURACIÓN DE MONITOREO ---
# Esto crea el endpoint /metrics automáticamente
Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": " -> ".join(str(x) for x in error["loc"][1:]), "message": error["msg"]} for error in exc.errors()]
    return JSONResponse(status_code=400, content={"detail": "Error de validación", "errors": errors})

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "Error de integridad: registro duplicado"})

app.include_router(auth.router)
app.include_router(planetas.router)

@app.get("/", tags=["Root"])
def root():
    return {"message": "API de Gestión de Planetas", "docs": "/docs", "metrics": "/metrics"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)