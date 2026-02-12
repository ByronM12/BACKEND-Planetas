import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Limpiar y preparar la base de datos antes de cada test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Crear usuarios de prueba
    db = TestingSessionLocal()
    admin = User(
        username="admin_test",
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        role="ADMIN",
        is_active=True
    )
    usuario = User(
        username="usuario_test",
        email="usuario@test.com",
        hashed_password=get_password_hash("usuario123"),
        role="USUARIO",
        is_active=True
    )
    db.add(admin)
    db.add(usuario)
    db.commit()
    db.close()
    
    yield
    
    Base.metadata.drop_all(bind=engine)


def get_admin_token():
    """Obtener token de administrador"""
    response = client.post(
        "/auth/login",
        json={"username": "admin_test", "password": "admin123"}
    )
    return response.json()["access_token"]


def get_usuario_token():
    """Obtener token de usuario normal"""
    response = client.post(
        "/auth/login",
        json={"username": "usuario_test", "password": "usuario123"}
    )
    return response.json()["access_token"]


class TestAuthentication:
    """Pruebas de autenticación y seguridad JWT"""
    
    def test_login_success_admin(self):
        """Test: Login exitoso con credenciales de admin"""
        response = client.post(
            "/auth/login",
            json={"username": "admin_test", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["role"] == "ADMIN"
    
    def test_login_success_usuario(self):
        """Test: Login exitoso con credenciales de usuario"""
        response = client.post(
            "/auth/login",
            json={"username": "usuario_test", "password": "usuario123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "USUARIO"
    
    def test_login_invalid_credentials(self):
        """Test: Login con credenciales incorrectas"""
        response = client.post(
            "/auth/login",
            json={"username": "admin_test", "password": "wrong_password"}
        )
        assert response.status_code == 401
        assert "incorrectos" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self):
        """Test: Login con usuario inexistente"""
        response = client.post(
            "/auth/login",
            json={"username": "noexiste", "password": "password"}
        )
        assert response.status_code == 401
    
    def test_access_protected_endpoint_without_token(self):
        """Test: Acceso a endpoint protegido sin token"""
        response = client.get("/planetas/")
        assert response.status_code == 403  # Sin credenciales
    
    def test_access_protected_endpoint_with_invalid_token(self):
        """Test: Acceso con token inválido"""
        response = client.get(
            "/planetas/",
            headers={"Authorization": "Bearer token_invalido"}
        )
        assert response.status_code == 401


class TestPlanetaCRUD:
    """Pruebas de operaciones CRUD de planetas"""
    
    def test_create_planeta_success_admin(self):
        """Test: Crear planeta correctamente como ADMIN"""
        token = get_admin_token()
        planeta_data = {
            "nombre": "Marte",
            "tipo": "Rocoso",
            "distanciaAlSol": 227.9,
            "numeroLunas": 2,
            "masa": 0.107,
            "estado": "Confirmado",
            "fechaDescubrimiento": "1610-01-01T00:00:00"
        }
        response = client.post(
            "/planetas/",
            json=planeta_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Marte"
        assert data["tipo"] == "Rocoso"
        assert data["numeroLunas"] == 2
        assert "id" in data
    
    def test_create_planeta_success_usuario(self):
        """Test: Usuario normal puede crear (registrar) planetas"""
        token = get_usuario_token()
        planeta_data = {
            "nombre": "Venus",
            "tipo": "Rocoso",
            "distanciaAlSol": 108.2,
            "numeroLunas": 0,
            "masa": 0.815,
            "estado": "Confirmado"
        }
        response = client.post(
            "/planetas/",
            json=planeta_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        assert response.json()["nombre"] == "Venus"
    
    def test_create_planeta_missing_required_fields(self):
        """Test: Error 400 - Campos obligatorios faltantes"""
        token = get_admin_token()
        planeta_data = {
            "distanciaAlSol": 227.9  # Falta nombre y tipo
        }
        response = client.post(
            "/planetas/",
            json=planeta_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        assert "validación" in response.json()["detail"].lower()
    
    def test_create_planeta_invalid_data_types(self):
        """Test: Error 400 - Tipos de datos incorrectos"""
        token = get_admin_token()
        planeta_data = {
            "nombre": "Júpiter",
            "tipo": "Gaseoso",
            "distanciaAlSol": "no es un número",  # Debe ser float
            "numeroLunas": "muchas"  # Debe ser int
        }
        response = client.post(
            "/planetas/",
            json=planeta_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
    
    def test_create_planeta_duplicate_name(self):
        """Test: Error 409 - Nombre duplicado"""
        token = get_admin_token()
        planeta_data = {
            "nombre": "Saturno",
            "tipo": "Gaseoso",
            "distanciaAlSol": 1433.5,
            "numeroLunas": 82
        }
        
        # Crear primer planeta
        response1 = client.post(
            "/planetas/",
            json=planeta_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response1.status_code == 201
        
        # Intentar crear planeta con mismo nombre
        response2 = client.post(
            "/planetas/",
            json=planeta_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response2.status_code == 409
        assert "ya existe" in response2.json()["detail"].lower()
    
    def test_list_planetas_admin(self):
        """Test: ADMIN puede listar todos los planetas"""
        token = get_admin_token()
        
        # Crear algunos planetas
        planetas = [
            {"nombre": "Tierra", "tipo": "Rocoso", "numeroLunas": 1},
            {"nombre": "Júpiter", "tipo": "Gaseoso", "numeroLunas": 79}
        ]
        for p in planetas:
            client.post("/planetas/", json=p, headers={"Authorization": f"Bearer {token}"})
        
        # Listar planetas
        response = client.get(
            "/planetas/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    def test_list_planetas_usuario_forbidden(self):
        """Test: USUARIO no puede listar planetas (403)"""
        token = get_usuario_token()
        response = client.get(
            "/planetas/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        assert "permissions" in response.json()["detail"].lower()
    
    def test_get_planeta_by_id_admin(self):
        """Test: ADMIN puede obtener planeta por ID"""
        token = get_admin_token()
        
        # Crear planeta
        create_response = client.post(
            "/planetas/",
            json={"nombre": "Neptuno", "tipo": "Gaseoso"},
            headers={"Authorization": f"Bearer {token}"}
        )
        planeta_id = create_response.json()["id"]
        
        # Obtener por ID
        response = client.get(
            f"/planetas/{planeta_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Neptuno"
    
    def test_get_planeta_by_id_usuario_forbidden(self):
        """Test: USUARIO no puede obtener planeta por ID"""
        admin_token = get_admin_token()
        usuario_token = get_usuario_token()
        
        # Admin crea planeta
        create_response = client.post(
            "/planetas/",
            json={"nombre": "Urano", "tipo": "Gaseoso"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        planeta_id = create_response.json()["id"]
        
        # Usuario intenta obtener
        response = client.get(
            f"/planetas/{planeta_id}",
            headers={"Authorization": f"Bearer {usuario_token}"}
        )
        assert response.status_code == 403
    
    def test_get_planeta_not_found(self):
        """Test: Error 404 - Planeta no encontrado"""
        token = get_admin_token()
        response = client.get(
            "/planetas/9999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()
    
    def test_update_planeta_admin(self):
        """Test: ADMIN puede actualizar planeta"""
        token = get_admin_token()
        
        # Crear planeta
        create_response = client.post(
            "/planetas/",
            json={"nombre": "Plutón", "tipo": "Enano", "numeroLunas": 5},
            headers={"Authorization": f"Bearer {token}"}
        )
        planeta_id = create_response.json()["id"]
        
        # Actualizar
        update_data = {"numeroLunas": 6, "estado": "Confirmado"}
        response = client.put(
            f"/planetas/{planeta_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["numeroLunas"] == 6
        assert data["estado"] == "Confirmado"
    
    def test_update_planeta_usuario_forbidden(self):
        """Test: USUARIO no puede actualizar planetas"""
        admin_token = get_admin_token()
        usuario_token = get_usuario_token()
        
        # Admin crea planeta
        create_response = client.post(
            "/planetas/",
            json={"nombre": "Mercurio", "tipo": "Rocoso"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        planeta_id = create_response.json()["id"]
        
        # Usuario intenta actualizar
        response = client.put(
            f"/planetas/{planeta_id}",
            json={"numeroLunas": 1},
            headers={"Authorization": f"Bearer {usuario_token}"}
        )
        assert response.status_code == 403
    
    def test_delete_planeta_admin(self):
        """Test: ADMIN puede eliminar planeta"""
        token = get_admin_token()
        
        # Crear planeta
        create_response = client.post(
            "/planetas/",
            json={"nombre": "Planeta X", "tipo": "Enano"},
            headers={"Authorization": f"Bearer {token}"}
        )
        planeta_id = create_response.json()["id"]
        
        # Eliminar
        response = client.delete(
            f"/planetas/{planeta_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "eliminado" in response.json()["message"].lower()
        
        # Verificar que no existe
        get_response = client.get(
            f"/planetas/{planeta_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404
    
    def test_delete_planeta_usuario_forbidden(self):
        """Test: USUARIO no puede eliminar planetas"""
        admin_token = get_admin_token()
        usuario_token = get_usuario_token()
        
        # Admin crea planeta
        create_response = client.post(
            "/planetas/",
            json={"nombre": "Kepler-452b", "tipo": "Rocoso"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        planeta_id = create_response.json()["id"]
        
        # Usuario intenta eliminar
        response = client.delete(
            f"/planetas/{planeta_id}",
            headers={"Authorization": f"Bearer {usuario_token}"}
        )
        assert response.status_code == 403


class TestValidations:
    """Pruebas de validaciones de datos"""
    
    def test_nombre_vacio(self):
        """Test: Validación nombre vacío"""
        token = get_admin_token()
        response = client.post(
            "/planetas/",
            json={"nombre": "", "tipo": "Rocoso"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
    
    def test_tipo_invalido(self):
        """Test: Tipo de planeta inválido"""
        token = get_admin_token()
        response = client.post(
            "/planetas/",
            json={"nombre": "Test", "tipo": "TipoInvalido"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
    
    def test_numero_lunas_negativo(self):
        """Test: Número de lunas negativo"""
        token = get_admin_token()
        response = client.post(
            "/planetas/",
            json={"nombre": "Test", "tipo": "Rocoso", "numeroLunas": -5},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
