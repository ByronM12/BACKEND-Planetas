from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class TipoPlaneta(str, Enum):
    ROCOSO = "Rocoso"
    GASEOSO = "Gaseoso"
    ENANO = "Enano"


class EstadoPlaneta(str, Enum):
    CONFIRMADO = "Confirmado"
    EN_ESTUDIO = "En estudio"


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USUARIO = "USUARIO"


# Schemas de Usuario
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole = UserRole.USUARIO


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# Schemas de Planeta
class PlanetaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre único del planeta")
    tipo: TipoPlaneta = Field(..., description="Tipo de planeta: Rocoso, Gaseoso o Enano")
    distanciaAlSol: Optional[float] = Field(None, ge=0, description="Distancia al Sol en millones de km")
    numeroLunas: Optional[int] = Field(0, ge=0, description="Número de lunas")
    masa: Optional[float] = Field(None, gt=0, description="Masa en masas terrestres (debe ser mayor que 0)")
    estado: EstadoPlaneta = Field(EstadoPlaneta.EN_ESTUDIO, description="Estado: Confirmado o En estudio")
    fechaDescubrimiento: Optional[datetime] = Field(None, description="Fecha de descubrimiento")

    @field_validator('nombre')
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El nombre del planeta no puede estar vacío')
        return v.strip()


class PlanetaCreate(PlanetaBase):
    pass


class PlanetaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[TipoPlaneta] = None
    distanciaAlSol: Optional[float] = Field(None, ge=0)
    numeroLunas: Optional[int] = Field(None, ge=0)
    masa: Optional[float] = Field(None, ge=0)
    estado: Optional[EstadoPlaneta] = None
    fechaDescubrimiento: Optional[datetime] = None

    @field_validator('nombre')
    @classmethod
    def nombre_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError('El nombre del planeta no puede estar vacío')
        return v.strip() if v else v


class PlanetaResponse(PlanetaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PlanetaListResponse(BaseModel):
    total: int
    planetas: list[PlanetaResponse]


class ErrorResponse(BaseModel):
    detail: str


class ValidationErrorResponse(BaseModel):
    detail: list[dict]
