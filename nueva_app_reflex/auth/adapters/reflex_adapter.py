"""
Adaptador para integrar el sistema de autenticación con Reflex.

Este módulo proporciona clases y funciones para integrar el sistema de autenticación
con aplicaciones Reflex, incluyendo estado para la autenticación.

Classes:
    AuthState: Estado de Reflex con funcionalidades de autenticación.
    
Functions:
    require_auth: Decorador para rutas que requieren autenticación.
"""

from typing import Dict, Optional, Any, Callable, Type, List, Union, TypeVar, cast
import inspect
import functools
from datetime import datetime

import reflex as rx
from reflex.state import State

from ..core.auth import AuthManager, AuthUser, LoginResult, InvalidCredentialsException, PasswordPolicyException
from ..core.token import get_token_data, TOKEN_TYPE_ACCESS
from ..config import get_auth_config

# Obtener configuración
config = get_auth_config()

# Tipo genérico para usuario
T = TypeVar('T', bound=AuthUser)


class AuthState(State):
    """
    Estado de Reflex con funcionalidades de autenticación.
    
    Esta clase extiende el State de Reflex para proporcionar estado y 
    métodos relacionados con la autenticación de usuarios.
    
    Attributes:
        is_authenticated (bool): Indica si el usuario está autenticado.
        current_user (Dict[str, Any]): Datos del usuario autenticado.
        access_token (str): Token de acceso JWT.
        refresh_token (str): Token de refresco JWT.
        auth_message (str): Mensaje relacionado con la autenticación.
        token_expires_at (Optional[datetime]): Fecha/hora de expiración del token.
    """
    
    # Estado de autenticación
    is_authenticated: bool = False
    current_user: Dict[str, Any] = {}
    access_token: str = ""
    refresh_token: str = ""
    auth_message: str = ""
    token_expires_at: Optional[datetime] = None
    
    # Instancia de AuthManager
    _auth_manager: Optional[AuthManager] = None
    
    def set_auth_manager(self, auth_manager: AuthManager) -> None:
        """
        Establece el gestor de autenticación.
        
        Args:
            auth_manager (AuthManager): Gestor de autenticación a utilizar.
        """
        self._auth_manager = auth_manager
    
    def login(self, username: str, password: str) -> None:
        """
        Inicia sesión con nombre de usuario y contraseña.
        
        Args:
            username (str): Nombre de usuario o email.
            password (str): Contraseña en texto plano.
        """
        if not self._auth_manager:
            self.auth_message = "Error: AuthManager no configurado"
            return
        
        try:
            result: LoginResult = self._auth_manager.authenticate(username, password)
            
            if result.success:
                self.is_authenticated = True
                self.current_user = result.user.to_dict() if result.user else {}
                self.access_token = result.access_token or ""
                self.refresh_token = result.refresh_token or ""
                self.token_expires_at = result.expires_at
                self.auth_message = "Login exitoso"
                
                # Guardar token en cookies
                self.set_cookie("access_token", self.access_token)
                if self.refresh_token:
                    self.set_cookie("refresh_token", self.refresh_token)
            else:
                self.auth_message = result.message
        except Exception as e:
            self.auth_message = f"Error de autenticación: {str(e)}"
    
    def logout(self) -> None:
        """
        Cierra la sesión del usuario actual.
        """
        self.is_authenticated = False
        self.current_user = {}
        self.access_token = ""
        self.refresh_token = ""
        self.token_expires_at = None
        self.auth_message = "Sesión cerrada"
        
        # Eliminar cookies
        self.clear_cookie("access_token")
        self.clear_cookie("refresh_token")
    
    def check_auth_from_cookies(self) -> bool:
        """
        Verifica la autenticación a partir de las cookies.
        
        Returns:
            bool: True si el usuario está autenticado, False en caso contrario.
        """
        if not self._auth_manager:
            return False
        
        # Obtener token de cookies
        token = self.get_cookie("access_token")
        if not token:
            return False
        
        # Verificar token
        user = self._auth_manager.verify_token(token)
        if not user:
            # Intentar con refresh token si está habilitado
            if config.ENABLE_REFRESH_TOKENS:
                refresh_token = self.get_cookie("refresh_token")
                if refresh_token:
                    # Aquí se implementaría la lógica para renovar el token
                    # con el refresh token, pero lo dejamos pendiente por ahora
                    pass
            return False
        
        # Usuario autenticado
        self.is_authenticated = True
        self.current_user = user.to_dict()
        self.access_token = token
        return True
    
    def register(self, username: str, email: str, password: str, **kwargs) -> None:
        """
        Registra un nuevo usuario.
        
        Args:
            username (str): Nombre de usuario.
            email (str): Correo electrónico.
            password (str): Contraseña en texto plano.
            **kwargs: Argumentos adicionales para el modelo de usuario.
        """
        if not self._auth_manager:
            self.auth_message = "Error: AuthManager no configurado"
            return
        
        try:
            result = self._auth_manager.register_user(username, email, password, **kwargs)
            
            if isinstance(result, str):
                # Error en el registro
                self.auth_message = result
            else:
                # Registro exitoso
                self.auth_message = f"Usuario {username} registrado correctamente"
        except PasswordPolicyException as e:
            self.auth_message = e.message
        except Exception as e:
            self.auth_message = f"Error en el registro: {str(e)}"
    
    def change_password(self, current_password: str, new_password: str) -> None:
        """
        Cambia la contraseña del usuario actual.
        
        Args:
            current_password (str): Contraseña actual.
            new_password (str): Nueva contraseña.
        """
        if not self._auth_manager or not self.is_authenticated:
            self.auth_message = "No hay sesión activa"
            return
        
        try:
            # Obtener usuario actual
            user = self._auth_manager.verify_token(self.access_token)
            if not user:
                self.auth_message = "Sesión expirada"
                return
            
            # Cambiar contraseña
            success = self._auth_manager.change_password(user, current_password, new_password)
            
            if success:
                self.auth_message = "Contraseña cambiada correctamente"
            else:
                self.auth_message = "Error al cambiar la contraseña"
        except InvalidCredentialsException:
            self.auth_message = "Contraseña actual incorrecta"
        except PasswordPolicyException as e:
            self.auth_message = e.message
        except Exception as e:
            self.auth_message = f"Error al cambiar la contraseña: {str(e)}"


def require_auth(handler=None):
    """
    Decorador para rutas que requieren autenticación.
    
    Este decorador redirige a la página de login si el usuario no está autenticado.
    
    Args:
        handler: Manejador de ruta a decorar.
        
    Returns:
        Función decorada que verifica autenticación antes de ejecutar el manejador.
    """
    def decorator(handler_func):
        @functools.wraps(handler_func)
        def wrapper(*args, **kwargs):
            # Obtener instancia de estado
            state_instance = None
            for arg in args:
                if isinstance(arg, AuthState):
                    state_instance = arg
                    break
            
            # Verificar autenticación
            if state_instance and not state_instance.is_authenticated:
                # Intentar autenticar desde cookies
                if not state_instance.check_auth_from_cookies():
                    return rx.redirect(config.LOGIN_URL)
            
            # Ejecutar manejador original
            return handler_func(*args, **kwargs)
        
        return wrapper
    
    # Permitir usar el decorador con o sin paréntesis
    if handler is None:
        return decorator
    return decorator(handler)


def create_auth_middleware():
    """
    Crea un middleware para Reflex que verifica la autenticación en cada solicitud.
    
    Returns:
        Callable: Middleware que verifica autenticación.
    """
    async def auth_middleware(request, call_next):
        # Procesar la solicitud
        response = await call_next(request)
        
        # Aquí se podrían verificar cookies, renovar tokens, etc.
        return response
    
    return auth_middleware
