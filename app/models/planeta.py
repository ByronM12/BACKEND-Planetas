from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TipoPlaneta(str, enum.Enum):
    ROCOSO = "Rocoso"
    GASEOSO = "Gaseoso"
    ENANO = "Enano"


class EstadoPlaneta(str, enum.Enum):
    CONFIRMADO = "Confirmado"
    EN_ESTUDIO = "En estudio"


class Planeta(Base):
    __tablename__ = "planetas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    tipo = Column(SQLEnum(TipoPlaneta), nullable=False)
    distanciaAlSol = Column(Float, nullable=True)  # en millones de km
    numeroLunas = Column(Integer, default=0)
    masa = Column(Float, nullable=True)  # en masas terrestres
    estado = Column(SQLEnum(EstadoPlaneta), default=EstadoPlaneta.EN_ESTUDIO)
    fechaDescubrimiento = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
