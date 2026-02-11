# 🌍 API REST - Sistema de Gestión de Planetas

API REST completa con FastAPI, autenticación JWT, control de roles y validaciones.

## 🚀 Características

- ✅ CRUD completo de planetas
- 🔐 Autenticación JWT
- 👥 Control de acceso por roles (ADMIN / USUARIO)
- ✔️ Validaciones de datos
- 📝 Documentación automática con Swagger
- 🧪 Pruebas unitarias completas
- ⚡ Pruebas de carga con JMeter
- 🐳 Listo para Docker
- 🚂 Configurado para Railway

## 📋 Requisitos

- Python 3.12+
- pip

## 🛠️ Instalación Local

### 1. Clonar el repositorio
```bash
cd backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (opcional)
```bash
cp .env.example .env
# Editar .env si es necesario
```

### 5. Ejecutar la aplicación
```bash
uvicorn app.main:app --reload
```

La API estará disponible en: `http://localhost:8000`

## 📚 Documentación API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 👤 Usuarios de Prueba

La aplicación se inicializa automáticamente con dos usuarios:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | ADMIN |
| usuario | usuario123 | USUARIO |

## 🔑 Autenticación

### 1. Obtener Token
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

Respuesta:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@planetas.com",
    "role": "ADMIN"
  }
}
```

### 2. Usar Token en Requests
```bash
GET /planetas/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 🌐 Endpoints

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrar nuevo usuario

### Planetas

| Método | Endpoint | Rol | Descripción |
|--------|----------|-----|-------------|
| POST | /planetas/ | ADMIN, USUARIO | Crear planeta |
| GET | /planetas/ | ADMIN | Listar todos |
| GET | /planetas/{id} | ADMIN | Obtener por ID |
| PUT | /planetas/{id} | ADMIN | Actualizar |
| DELETE | /planetas/{id} | ADMIN | Eliminar |

## 📝 Ejemplos de Uso

### Crear Planeta
```bash
POST /planetas/
Authorization: Bearer {token}
Content-Type: application/json

{
  "nombre": "Marte",
  "tipo": "Rocoso",
  "distanciaAlSol": 227.9,
  "numeroLunas": 2,
  "masa": 0.107,
  "estado": "Confirmado",
  "fechaDescubrimiento": "1610-01-01T00:00:00"
}
```

### Listar Planetas
```bash
GET /planetas/
Authorization: Bearer {token}
```

### Actualizar Planeta
```bash
PUT /planetas/1
Authorization: Bearer {token}
Content-Type: application/json

{
  "numeroLunas": 3,
  "estado": "En estudio"
}
```

## 🧪 Ejecutar Pruebas

### Pruebas Unitarias
```bash
pytest app/tests/test_api.py -v
```

### Pruebas con Coverage
```bash
pytest app/tests/test_api.py --cov=app --cov-report=html
```

## ⚡ Pruebas de Carga (JMeter)

### Requisitos
- Apache JMeter instalado

### Ejecutar pruebas
```bash
jmeter -n -t jmeter/planetas_load_test.jmx -l resultados.jtl
```

### Configuración de la prueba
- **Usuarios concurrentes**: 50
- **Ramp-up time**: 10 segundos
- **Iteraciones**: 10 por usuario
- **Total de requests**: ~1,500

## 🐳 Docker

### Construir imagen
```bash
docker build -t planetas-api .
```

### Ejecutar contenedor
```bash
docker run -p 8000:8000 planetas-api
```

## 🚂 Despliegue en Railway

### Opción 1: Desde GitHub
1. Conectar tu repositorio de GitHub a Railway
2. Railway detectará automáticamente el `Dockerfile`
3. El despliegue será automático

### Opción 2: Railway CLI
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Inicializar proyecto
railway init

# Desplegar
railway up
```

### Variables de Entorno en Railway
No es necesario configurar variables especiales. La aplicación usa SQLite por defecto.

## 📊 Monitoreo con UptimeRobot

1. Crear cuenta en https://uptimerobot.com
2. Agregar nuevo monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://tu-app.railway.app/health`
   - **Monitoring Interval**: 5 minutos
   - **Monitor Timeout**: 30 segundos

## 🔒 Seguridad

- JWT con expiración de 30 minutos
- Contraseñas hasheadas con bcrypt
- Validación de roles en cada endpoint
- CORS configurado
- Validación de entrada con Pydantic

## ⚠️ Códigos de Error

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - No autenticado |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Registro duplicado |
| 422 | Unprocessable Entity - Error de validación |
| 500 | Internal Server Error |

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── api/
│   │   ├── auth.py          # Endpoints de autenticación
│   │   └── planetas.py      # Endpoints de planetas
│   ├── core/
│   │   ├── config.py        # Configuración
│   │   ├── database.py      # Base de datos
│   │   └── security.py      # JWT y seguridad
│   ├── models/
│   │   ├── user.py          # Modelo de Usuario
│   │   └── planeta.py       # Modelo de Planeta
│   ├── schemas/
│   │   └── schemas.py       # Schemas Pydantic
│   ├── services/
│   │   ├── auth_service.py  # Lógica de autenticación
│   │   └── planeta_service.py # Lógica de planetas
│   ├── tests/
│   │   └── test_api.py      # Pruebas unitarias
│   └── main.py              # Aplicación principal
├── jmeter/
│   └── planetas_load_test.jmx # Plan de pruebas JMeter
├── Dockerfile
├── requirements.txt
├── railway.json
└── README.md
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 👨‍💻 Autor

Sistema de Gestión de Planetas - 2025
