# Sistema de Autenticación Seguro

Este módulo proporciona un sistema de autenticación completo, seguro y modular que puede ser integrado fácilmente en cualquier aplicación Python, incluyendo aplicaciones Reflex y FastAPI.

## Características

- **Gestión segura de contraseñas** con Argon2 (ganador de la competición de hasheo de contraseñas)
- **Autenticación basada en tokens JWT** con soporte para tokens de acceso y refresco
- **Protección contra ataques comunes** como timing attacks, inyección SQL, etc.
- **Verificación de email** y recuperación de contraseña
- **Integración con múltiples frameworks** a través de adaptadores (Reflex, FastAPI)
- **Configuración flexible** a través de variables de entorno o código
- **Rate limiting** para proteger contra ataques de fuerza bruta
- **Documentación completa** con docstrings, comentarios y ejemplos de uso

## Estructura del Módulo

```
auth/
├── __init__.py             # Punto de entrada del módulo
├── config.py               # Configuración centralizada
├── README.md               # Documentación
├── adapters/               # Adaptadores para diferentes frameworks
│   ├── __init__.py
│   ├── reflex_adapter.py   # Integración con Reflex
│   └── fastapi_adapter.py  # Integración con FastAPI
├── core/                   # Funcionalidades principales
│   ├── auth.py             # Gestión de autenticación
│   ├── password.py         # Gestión de contraseñas
│   └── token.py            # Gestión de tokens
└── utils/                  # Utilidades
    ├── model_adapter.py    # Adaptadores para modelos existentes
    └── example_integration.py # Ejemplos de integración
```

## Requisitos

Para usar este módulo se requieren las siguientes dependencias:

```
pyjwt>=2.6.0
argon2-cffi>=21.3.0
pydantic>=1.10.7
```

## Instalación

1. Asegúrate de tener las dependencias instaladas:

```bash
pip install pyjwt argon2-cffi pydantic
```

2. Copia la carpeta `auth` a tu proyecto.

## Configuración

El sistema puede configurarse a través de variables de entorno o mediante código:

```python
from nueva_app_reflex.auth.config import configure_auth

# Configuración mediante diccionario
configure_auth({
    "SECRET_KEY": "tu_clave_secreta_aqui",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    "PASSWORD_MIN_LENGTH": 8
})

# O mediante variables de entorno:
# AUTH_SECRET_KEY=tu_clave_secreta
# AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=30
# AUTH_PASSWORD_MIN_LENGTH=8
```

## Ejemplos de Uso

### Integración con Reflex

```python
from nueva_app_reflex.auth.core.auth import AuthManager
from nueva_app_reflex.auth.adapters.reflex_adapter import AuthState, require_auth
from nueva_app_reflex.auth.utils.model_adapter import adapt_usuario_model

# Crear AuthManager
auth_manager = AuthManager(
    user_model=adapt_usuario_model,
    get_user_by_username=get_user_by_username,
    get_user_by_email=get_user_by_email,
    save_user=save_user,
    update_user=update_user
)

# Extender el State con autenticación
class AppState(AuthState):
    def __init__(self):
        super().__init__()
        self.set_auth_manager(auth_manager)

# Página protegida
@require_auth
def pagina_protegida(state: AppState):
    return rx.fragment(
        rx.heading(f"Bienvenido, {state.current_user.get('username')}"),
        rx.text("Esta página solo es accesible para usuarios autenticados")
    )
```

### Integración con FastAPI

```python
from fastapi import FastAPI, Depends
from nueva_app_reflex.auth.core.auth import AuthManager
from nueva_app_reflex.auth.adapters.fastapi_adapter import create_auth_router, get_current_user

# Crear AuthManager
auth_manager = AuthManager(
    user_model=adapt_usuario_model,
    get_user_by_username=get_user_by_username,
    get_user_by_email=get_user_by_email,
    save_user=save_user,
    update_user=update_user
)

# Crear la aplicación FastAPI
app = FastAPI()

# Incluir router de autenticación
auth_router = create_auth_router(auth_manager)
app.include_router(auth_router, prefix="/auth")

# Endpoint protegido
@app.get("/protected")
async def protected_route(user = Depends(lambda: get_current_user(auth_manager))):
    return {"message": f"Bienvenido, {user.username}"}
```

## Seguridad

Este sistema implementa las mejores prácticas de seguridad:

- Hasheo de contraseñas con Argon2 (considerado el más seguro)
- Protección contra timing attacks en la verificación de contraseñas
- Validación de contraseñas con requisitos de complejidad
- Tokens JWT con tiempos de expiración configurables
- Rate limiting para prevenir ataques de fuerza bruta
- Cookies HttpOnly y Secure para almacenamiento seguro de tokens
- Validación de entradas con Pydantic
- Manejo adecuado de errores y excepciones

## Adaptación a Otros Proyectos

Para adaptar este sistema a otro proyecto:

1. Copia la carpeta `auth` a tu proyecto
2. Adapta tus modelos de usuario usando los adaptadores proporcionados
3. Configura el sistema según tus necesidades
4. Integra con tu framework usando los adaptadores correspondientes

Ver `utils/example_integration.py` para ejemplos completos.

## Licencia

Este código es de uso libre para proyectos personales y comerciales.
