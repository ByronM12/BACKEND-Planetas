from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.api import auth, planetas

# --- MONITOREO ---
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejador del ciclo de vida de la aplicación."""
    print("🚀 Iniciando aplicación en Docker...")
    yield
    print("👋 Apagando aplicación...")

app = FastAPI(
    title="Sistema de Gestión de Planetas",
    description="API REST para la gestión de planetas con monitoreo y pruebas de carga.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CONFIGURACIÓN DE CORS ---
# Permitir "*" es vital para que Vercel y JMeter no sean bloqueados
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE MONITOREO (Prometheus) ---
# Debe ir después de CORS para registrar peticiones externas
Instrumentator().instrument(app).expose(app)

# Manejadores de Excepciones (Para mejores reportes en JMeter)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": " -> ".join(str(x) for x in error["loc"][1:]), "message": error["msg"]} for error in exc.errors()]
    return JSONResponse(status_code=400, content={"detail": "Error de validación", "errors": errors})

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "Error de integridad: registro duplicado"})

# Rutas
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
    # Se usa 0.0.0.0 para que sea accesible desde fuera del contenedor Docker
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)