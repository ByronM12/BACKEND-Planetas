from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.models.user import User
from app.schemas.schemas import (
    PlanetaCreate, 
    PlanetaUpdate, 
    PlanetaResponse,
    PlanetaListResponse
)
from app.services.planeta_service import PlanetaService

router = APIRouter(prefix="/planetas", tags=["Planetas"])


@router.post(
    "/",
    response_model=PlanetaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo planeta",
    description="Crea un nuevo planeta. **ADMIN**: puede crear. **USUARIO**: puede crear (registrar)."
)
def create_planeta(
    planeta: PlanetaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear un nuevo planeta.
    
    - **Roles permitidos**: ADMIN y USUARIO
    - **Validaciones**:
        - Nombre único (no duplicado)
        - Campos obligatorios: nombre, tipo
        - Tipos de datos correctos
    
    **Errores posibles**:
    - 400: Campos obligatorios vacíos o tipos de datos incorrectos
    - 409: Planeta con nombre duplicado
    - 401: No autenticado
    """
    return PlanetaService.create_planeta(db, planeta)


@router.get(
    "/",
    response_model=List[PlanetaResponse],
    summary="Listar todos los planetas",
    description="Lista todos los planetas. **Solo ADMIN**."
)
def list_planetas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Listar todos los planetas.
    
    - **Rol requerido**: ADMIN
    - **Parámetros**:
        - skip: número de registros a omitir (paginación)
        - limit: número máximo de registros a devolver
    
    **Errores posibles**:
    - 403: Usuario sin permisos suficientes (no es ADMIN)
    - 401: No autenticado
    """
    planetas = PlanetaService.get_all_planetas(db, skip=skip, limit=limit)
    return planetas


@router.get(
    "/{planeta_id}",
    response_model=PlanetaResponse,
    summary="Obtener planeta por ID",
    description="Obtiene un planeta específico por su ID. **Solo ADMIN**."
)
def get_planeta(
    planeta_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Obtener un planeta por su ID.
    
    - **Rol requerido**: ADMIN
    - **Parámetros**:
        - planeta_id: ID del planeta a consultar
    
    **Errores posibles**:
    - 404: Planeta no encontrado
    - 403: Usuario sin permisos suficientes (no es ADMIN)
    - 401: No autenticado
    """
    return PlanetaService.get_planeta_by_id(db, planeta_id)


@router.put(
    "/{planeta_id}",
    response_model=PlanetaResponse,
    summary="Actualizar un planeta",
    description="Actualiza un planeta existente. **Solo ADMIN**."
)
def update_planeta(
    planeta_id: int,
    planeta: PlanetaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Actualizar un planeta existente.
    
    - **Rol requerido**: ADMIN
    - **Parámetros**:
        - planeta_id: ID del planeta a actualizar
        - planeta: datos a actualizar (campos opcionales)
    
    **Validaciones**:
    - Si se actualiza el nombre, debe ser único
    - Tipos de datos correctos
    
    **Errores posibles**:
    - 404: Planeta no encontrado
    - 409: Nombre duplicado (si se intenta cambiar a un nombre ya existente)
    - 400: Tipos de datos incorrectos
    - 403: Usuario sin permisos suficientes (no es ADMIN)
    - 401: No autenticado
    """
    return PlanetaService.update_planeta(db, planeta_id, planeta)


@router.delete(
    "/{planeta_id}",
    summary="Eliminar un planeta",
    description="Elimina un planeta. **Solo ADMIN**."
)
def delete_planeta(
    planeta_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Eliminar un planeta.
    
    - **Rol requerido**: ADMIN
    - **Parámetros**:
        - planeta_id: ID del planeta a eliminar
    
    **Errores posibles**:
    - 404: Planeta no encontrado
    - 403: Usuario sin permisos suficientes (no es ADMIN)
    - 401: No autenticado
    """
    return PlanetaService.delete_planeta(db, planeta_id)
