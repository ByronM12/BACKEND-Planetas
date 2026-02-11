from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import Token, LoginRequest, UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=dict)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint de login para obtener el token JWT.
    
    Usuarios de prueba:
    - Admin: username=admin, password=admin123
    - Usuario: username=usuario, password=usuario123
    """
    return AuthService.login(db, login_data)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario.
    Solo disponible para desarrollo.
    """
    return AuthService.create_user(db, user)
