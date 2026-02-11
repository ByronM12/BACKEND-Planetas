from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.core.database import init_db
from app.api import auth, planetas


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manejador del ciclo de vida de la aplicación para eventos de inicio y apagado.
    """
    print("🚀 Iniciando aplicación y base de datos...")
    init_db()
    yield
    print("👋 Apagando aplicación...")

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Gestión de Planetas",
    description="""
    API REST para la gestión de planetas con autenticación JWT y control de roles.
    
    ## Autenticación
    
    Todos los endpoints (excepto /auth/login) requieren autenticación mediante JWT.
    
    ### Usuarios de prueba:
    - **Admin**: username=`admin`, password=`admin123`
    - **Usuario**: username=`usuario`, password=`usuario123`
    
    ### Cómo autenticarse:
    1. Hacer POST a `/auth/login` con las credenciales
    2. Copiar el `access_token` de la respuesta
    3. Hacer clic en el botón "Authorize" arriba
    4. Pegar el token (sin "Bearer")
    5. Los endpoints protegidos ahora funcionarán
    
    ## Roles
    
    - **ADMIN**: Acceso completo (crear, listar, obtener, actualizar, eliminar)
    - **USUARIO**: Solo puede crear (registrar) planetas
    
    ## Errores
    
    - **400 Bad Request**: Datos inválidos o campos obligatorios faltantes
    - **401 Unauthorized**: No autenticado o token inválido
    - **403 Forbidden**: Sin permisos suficientes
    - **409 Conflict**: Registro duplicado (nombre de planeta repetido)
    - **404 Not Found**: Recurso no encontrado
    """,
    version="1.0.0",
    contact={
        "name": "Sistema de Planetas",
        "email": "admin@planetas.com"
    },
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Manejador de errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"][1:])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Error de validación en los datos enviados",
            "errors": errors
        }
    )


# Manejador de errores de integridad
@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Error de integridad: registro duplicado"}
    )


# Incluir routers
app.include_router(auth.router)
app.include_router(planetas.router)


# Ruta raíz
@app.get("/", tags=["Root"])
def root():
    return {
        "message": "API de Gestión de Planetas",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Health check
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "planetas-api",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
