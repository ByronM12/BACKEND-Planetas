from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Usar SQLite para Railway (más simple para deployment)
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Solo para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializar la base de datos con usuarios de prueba"""
    from app.models.user import User
    from app.models.planeta import Planeta
    from app.core.security import get_password_hash
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Crear usuarios si no existen
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@planetas.com",
                hashed_password=get_password_hash("admin123"),
                role="ADMIN",
                is_active=True
            )
            db.add(admin)
        
        usuario = db.query(User).filter(User.username == "usuario").first()
        if not usuario:
            usuario = User(
                username="usuario",
                email="usuario@planetas.com",
                hashed_password=get_password_hash("usuario123"),
                role="USUARIO",
                is_active=True
            )
            db.add(usuario)
        
        db.commit()
        print("✅ Base de datos inicializada correctamente")
        print("👤 Usuario Admin: admin / admin123")
        print("👤 Usuario Normal: usuario / usuario123")
        
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        db.rollback()
    finally:
        db.close()
