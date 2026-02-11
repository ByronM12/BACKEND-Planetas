import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.schemas.schemas import UserCreate, LoginRequest, UserRole
from app.models.user import User


class TestAuthServiceUnitTests:
    """Pruebas unitarias del servicio de autenticación"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la sesión de base de datos"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_user(self):
        """Usuario mock para pruebas"""
        return User(
            id=1,
            username="testuser",
            email="test@test.com",
            hashed_password="$2b$12$precomputedhashfortesting",  # Hash simulado
            role="USUARIO",
            is_active=True
        )
    
    @pytest.fixture
    def mock_admin_user(self):
        """Usuario admin mock para pruebas"""
        return User(
            id=2,
            username="admin",
            email="admin@test.com",
            hashed_password="$2b$12$precomputedhashfortesting",  # Hash simulado
            role="ADMIN",
            is_active=True
        )
    
    # ===== PRUEBAS: create_user =====
    
    def test_create_user_success(self, mock_db):
        """✓ Crear usuario exitosamente"""
        user_data = UserCreate(
            username="newuser",
            email="new@test.com",
            password="password123",
            role=UserRole.USUARIO
        )
        
        # Mock del query - usuario y email no existen
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [None, None]  # No existe usuario ni email
        
        # Mock de get_password_hash para evitar bcrypt
        with patch('app.services.auth_service.get_password_hash', return_value="hashed_password"):
            # Ejecutar
            result = AuthService.create_user(mock_db, user_data)
            
            # Verificar
            assert result.username == "newuser"
            assert result.email == "new@test.com"
            assert result.role == "USUARIO"
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
    
    def test_create_user_username_already_exists(self, mock_db, mock_user):
        """✗ Error si el username ya existe"""
        user_data = UserCreate(
            username="testuser",
            email="new@test.com",
            password="password123"
        )
        
        # Mock: username existe
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user  # Ya existe
        
        # Verificar que lanza excepción
        with pytest.raises(HTTPException) as exc_info:
            AuthService.create_user(mock_db, user_data)
        
        assert exc_info.value.status_code == 409
        assert "registrado" in exc_info.value.detail.lower()
    
    def test_create_user_email_already_exists(self, mock_db, mock_user):
        """✗ Error si el email ya existe"""
        user_data = UserCreate(
            username="newuser",
            email="test@test.com",
            password="password123"
        )
        
        # Mock: username no existe, pero email sí
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [None, mock_user]  # Email existe
        
        with pytest.raises(HTTPException) as exc_info:
            AuthService.create_user(mock_db, user_data)
        
        assert exc_info.value.status_code == 409
        assert "email" in exc_info.value.detail.lower()
    
    # ===== PRUEBAS: authenticate_user =====
    
    def test_authenticate_user_success(self, mock_db, mock_user):
        """✓ Autenticar usuario exitosamente"""
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        with patch('app.services.auth_service.verify_password', return_value=True):
            result = AuthService.authenticate_user(
                mock_db,
                "testuser",
                "password123"
            )
        
        assert result.username == "testuser"
        assert result.is_active is True
    
    def test_authenticate_user_not_found(self, mock_db):
        """✗ Error si usuario no existe"""
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            AuthService.authenticate_user(mock_db, "noexiste", "password")
        
        assert exc_info.value.status_code == 401
        assert "incorrectos" in exc_info.value.detail.lower()
    
    def test_authenticate_user_wrong_password(self, mock_db, mock_user):
        """✗ Error si la contraseña es incorrecta"""
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        with patch('app.services.auth_service.verify_password', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                AuthService.authenticate_user(
                    mock_db,
                    "testuser",
                    "wrongpassword"
                )
        
        assert exc_info.value.status_code == 401
        assert "incorrectos" in exc_info.value.detail.lower()
    
    def test_authenticate_user_inactive(self, mock_db):
        """✗ Error si el usuario está inactivo"""
        inactive_user = User(
            id=1,
            username="testuser",
            email="test@test.com",
            hashed_password="$2b$12$precomputedhashfortesting",  # Hash simulado
            role="USUARIO",
            is_active=False
        )
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = inactive_user
        
        with patch('app.services.auth_service.verify_password', return_value=True):
            with pytest.raises(HTTPException) as exc_info:
                AuthService.authenticate_user(mock_db, "testuser", "password123")
        
        assert exc_info.value.status_code == 403
        assert "inactivo" in exc_info.value.detail.lower()
    
    # ===== PRUEBAS: login =====
    
    def test_login_success(self, mock_db, mock_user):
        """✓ Login exitoso retorna token"""
        login_data = LoginRequest(
            username="testuser",
            password="password123"
        )
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        with patch('app.services.auth_service.verify_password', return_value=True):
            with patch('app.services.auth_service.create_access_token', return_value="mock_token_123"):
                result = AuthService.login(mock_db, login_data)
        
        assert "access_token" in result
        assert result["token_type"] == "bearer"
        assert result["user"]["username"] == "testuser"
        assert result["user"]["role"] == "USUARIO"
    
    def test_login_with_admin_user(self, mock_db, mock_admin_user):
        """✓ Login exitoso con usuario ADMIN"""
        login_data = LoginRequest(
            username="admin",
            password="admin123"
        )
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_admin_user
        
        with patch('app.services.auth_service.verify_password', return_value=True):
            with patch('app.services.auth_service.create_access_token', return_value="mock_token_admin"):
                result = AuthService.login(mock_db, login_data)
        
        assert result["user"]["role"] == "ADMIN"
    
    def test_login_failure_invalid_credentials(self, mock_db):
        """✗ Login falla con credenciales incorrectas"""
        login_data = LoginRequest(
            username="noexiste",
            password="wrongpass"
        )
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            AuthService.login(mock_db, login_data)
        
        assert exc_info.value.status_code == 401
