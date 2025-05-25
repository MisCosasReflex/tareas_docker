"""
Ejemplo de integración del sistema de autenticación con aplicaciones.

Este módulo proporciona ejemplos de cómo integrar el sistema de autenticación
con diferentes frameworks como Reflex y FastAPI. Incluye código de ejemplo
que puede ser copiado y adaptado para otras aplicaciones.

Ejemplos:
    - Configuración para Reflex
    - Configuración para FastAPI
    - Adaptación de modelos existentes
"""

from typing import Dict, Optional, Any, List, Union, cast
import os

# Ejemplo para Reflex
def setup_reflex_auth_example():
    """
    Configuración de ejemplo para integrar el sistema de autenticación con Reflex.
    
    Este es un código de referencia que debe ser adaptado a cada aplicación.
    """
    import reflex as rx
    from ..db.database import SessionLocal
    from ..db.models import Usuario
    from ..auth.config import configure_auth
    from ..auth.core.auth import AuthManager
    from ..auth.adapters.reflex_adapter import AuthState, require_auth
    from ..auth.utils.model_adapter import adapt_usuario_model
    
    # 1. Configurar el sistema de autenticación
    configure_auth({
        "SECRET_KEY": os.getenv("AUTH_SECRET_KEY", "tu_clave_secreta_aqui"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        "PASSWORD_MIN_LENGTH": 8
    })
    
    # 2. Definir funciones para acceder a los usuarios
    def get_user_by_username(username: str) -> Optional[adapt_usuario_model]:
        """Obtiene un usuario por su nombre de usuario."""
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(Usuario.nombre == username).first()
            if usuario:
                return adapt_usuario_model(usuario)
            return None
        finally:
            db.close()
    
    def get_user_by_email(email: str) -> Optional[adapt_usuario_model]:
        """Obtiene un usuario por su email."""
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(Usuario.email == email).first()
            if usuario:
                return adapt_usuario_model(usuario)
            return None
        finally:
            db.close()
    
    def save_user(user_data: Dict[str, Any]) -> None:
        """Guarda un nuevo usuario en la base de datos."""
        db = SessionLocal()
        try:
            # Crear usuario con los campos necesarios
            usuario = Usuario(
                nombre=user_data["username"],
                email=user_data["email"],
                password_hash=user_data["password_hash"],
                es_admin=user_data.get("es_admin", False)
            )
            db.add(usuario)
            db.commit()
        finally:
            db.close()
    
    def update_user(user) -> None:
        """Actualiza un usuario existente."""
        db = SessionLocal()
        try:
            # El objeto usuario ya está asociado a la sesión
            db.commit()
        finally:
            db.close()
    
    # 3. Crear el AuthManager
    auth_manager = AuthManager(
        user_model=adapt_usuario_model,
        get_user_by_username=get_user_by_username,
        get_user_by_email=get_user_by_email,
        save_user=save_user,
        update_user=update_user
    )
    
    # 4. Extender el State de la aplicación con autenticación
    class AppState(AuthState):
        """Estado de la aplicación que incluye autenticación."""
        
        def __init__(self):
            super().__init__()
            # Configurar AuthManager
            self.set_auth_manager(auth_manager)
        
        # Resto del estado de la aplicación
        # ...
    
    # 5. Ejemplo de una página protegida que requiere autenticación
    @require_auth
    def pagina_protegida(state: AppState):
        """Ejemplo de página que requiere autenticación."""
        return rx.fragment(
            rx.heading(f"Bienvenido, {state.current_user.get('username')}"),
            rx.text("Esta página solo es accesible para usuarios autenticados"),
            rx.button("Cerrar sesión", on_click=state.logout)
        )
    
    # 6. Ejemplo de página de login
    def pagina_login(state: AppState):
        """Ejemplo de página de login."""
        return rx.fragment(
            rx.vstack(
                rx.heading("Iniciar sesión"),
                rx.input(placeholder="Usuario o email", id="username"),
                rx.password(placeholder="Contraseña", id="password"),
                rx.button(
                    "Iniciar sesión", 
                    on_click=lambda: state.login(
                        rx.get_value("username"),
                        rx.get_value("password")
                    )
                ),
                rx.text(state.auth_message),
                spacing="4"
            )
        )


# Ejemplo para FastAPI
def setup_fastapi_auth_example():
    """
    Configuración de ejemplo para integrar el sistema de autenticación con FastAPI.
    
    Este es un código de referencia que debe ser adaptado a cada aplicación.
    """
    from fastapi import FastAPI, Depends
    from ..db.database import SessionLocal
    from ..db.models import Usuario
    from ..auth.config import configure_auth
    from ..auth.core.auth import AuthManager
    from ..auth.adapters.fastapi_adapter import create_auth_router, get_current_user
    from ..auth.utils.model_adapter import adapt_usuario_model
    
    # 1. Configurar el sistema de autenticación
    configure_auth({
        "SECRET_KEY": os.getenv("AUTH_SECRET_KEY", "tu_clave_secreta_aqui"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        "PASSWORD_MIN_LENGTH": 8
    })
    
    # 2. Definir funciones para acceder a los usuarios
    def get_user_by_username(username: str) -> Optional[adapt_usuario_model]:
        """Obtiene un usuario por su nombre de usuario."""
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(Usuario.nombre == username).first()
            if usuario:
                return adapt_usuario_model(usuario)
            return None
        finally:
            db.close()
    
    def get_user_by_email(email: str) -> Optional[adapt_usuario_model]:
        """Obtiene un usuario por su email."""
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(Usuario.email == email).first()
            if usuario:
                return adapt_usuario_model(usuario)
            return None
        finally:
            db.close()
    
    def save_user(user_data: Dict[str, Any]) -> None:
        """Guarda un nuevo usuario en la base de datos."""
        db = SessionLocal()
        try:
            # Crear usuario con los campos necesarios
            usuario = Usuario(
                nombre=user_data["username"],
                email=user_data["email"],
                password_hash=user_data["password_hash"],
                es_admin=user_data.get("es_admin", False)
            )
            db.add(usuario)
            db.commit()
        finally:
            db.close()
    
    def update_user(user) -> None:
        """Actualiza un usuario existente."""
        db = SessionLocal()
        try:
            # El objeto usuario ya está asociado a la sesión
            db.commit()
        finally:
            db.close()
    
    # 3. Crear el AuthManager
    auth_manager = AuthManager(
        user_model=adapt_usuario_model,
        get_user_by_username=get_user_by_username,
        get_user_by_email=get_user_by_email,
        save_user=save_user,
        update_user=update_user
    )
    
    # 4. Crear la aplicación FastAPI
    app = FastAPI(title="API con autenticación")
    
    # 5. Incluir el router de autenticación
    auth_router = create_auth_router(auth_manager)
    app.include_router(auth_router, prefix="/auth")
    
    # 6. Dependency para obtener el usuario actual
    async def get_current_user_dependency():
        return lambda: get_current_user(auth_manager)
    
    # 7. Ejemplo de endpoint protegido
    @app.get("/protected")
    async def protected_route(user = Depends(get_current_user_dependency())):
        """Endpoint protegido que requiere autenticación."""
        return {"message": f"Bienvenido, {user.username}", "data": user.to_dict()}
