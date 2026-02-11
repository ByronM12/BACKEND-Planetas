from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.planeta import Planeta
from app.schemas.schemas import PlanetaCreate, PlanetaUpdate


class PlanetaService:
    
    @staticmethod
    def get_all_planetas(db: Session, skip: int = 0, limit: int = 100) -> List[Planeta]:
        return db.query(Planeta).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_planeta_by_id(db: Session, planeta_id: int) -> Planeta:
        planeta = db.query(Planeta).filter(Planeta.id == planeta_id).first()
        if not planeta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planeta con ID {planeta_id} no encontrado"
            )
        return planeta
    
    @staticmethod
    def get_planeta_by_nombre(db: Session, nombre: str) -> Optional[Planeta]:
        return db.query(Planeta).filter(Planeta.nombre == nombre).first()
    
    @staticmethod
    def create_planeta(db: Session, planeta: PlanetaCreate) -> Planeta:
        # Verificar si ya existe un planeta con ese nombre
        existing_planeta = PlanetaService.get_planeta_by_nombre(db, planeta.nombre)
        if existing_planeta:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un planeta con el nombre '{planeta.nombre}'"
            )
        
        try:
            db_planeta = Planeta(
                nombre=planeta.nombre,
                tipo=planeta.tipo,
                distanciaAlSol=planeta.distanciaAlSol,
                numeroLunas=planeta.numeroLunas,
                masa=planeta.masa,
                estado=planeta.estado,
                fechaDescubrimiento=planeta.fechaDescubrimiento
            )
            
            db.add(db_planeta)
            db.commit()
            db.refresh(db_planeta)
            return db_planeta
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un planeta con el nombre '{planeta.nombre}'"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear el planeta: {str(e)}"
            )
    
    @staticmethod
    def update_planeta(db: Session, planeta_id: int, planeta_update: PlanetaUpdate) -> Planeta:
        db_planeta = PlanetaService.get_planeta_by_id(db, planeta_id)
        
        # Si se está actualizando el nombre, verificar que no exista otro planeta con ese nombre
        if planeta_update.nombre and planeta_update.nombre != db_planeta.nombre:
            existing = PlanetaService.get_planeta_by_nombre(db, planeta_update.nombre)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe otro planeta con el nombre '{planeta_update.nombre}'"
                )
        
        try:
            update_data = planeta_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_planeta, field, value)
            
            db.commit()
            db.refresh(db_planeta)
            return db_planeta
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error de integridad al actualizar el planeta"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar el planeta: {str(e)}"
            )
    
    @staticmethod
    def delete_planeta(db: Session, planeta_id: int) -> dict:
        db_planeta = PlanetaService.get_planeta_by_id(db, planeta_id)
        
        try:
            db.delete(db_planeta)
            db.commit()
            return {"message": f"Planeta '{db_planeta.nombre}' eliminado correctamente"}
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar el planeta: {str(e)}"
            )
