"""
Módulo principal para la autenticación de usuarios.

Este módulo proporciona clases y funciones para gestionar la autenticación 
de usuarios, integrando el manejo de contraseñas y tokens JWT. Es compatible
con diferentes frameworks web como Reflex y FastAPI.

Classes:
    AuthUser: Clase base para usuarios autenticables.
    AuthManager: Gestor de autenticación con métodos para login, verificación, etc.

Functions:
    authenticate_user: Autentica un usuario por sus credenciales.
    get_current_user: Obtiene el usuario actual a partir de un token.
"""

from typing import Dict, Optional, Any, Generic, TypeVar, Callable, Type, List, Union
from datetime import datetime, timedelta
import json
import base64
from abc import ABC, abstractmethod
import time
import uuid

from .password import hash_password, verify_password, password_meets_requirements
from .token import (
    create_access_token, 
    create_refresh_token,
    create_email_verification_token,
    verify_token,
    get_token_data,
    TOKEN_TYPE_ACCESS
)
from ..config import get_auth_config
from ...utils.logger import get_logger

# Configuración
config = get_auth_config()

# Inicializar logger
_logger = get_logger(__name__)

# Definir tipo genérico para modelos de usuario
T = TypeVar('T')

# Cache para rate limiting
_login_attempts: Dict[str, List[float]] = {}


class AuthException(Exception):
    """Excepción base para errores de autenticación."""
    pass


class InvalidCredentialsException(AuthException):
    """Excepción para credenciales inválidas."""
    def __init__(self, message: str = "Credenciales inválidas"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundException(AuthException):
    """Excepción para usuario no encontrado."""
    def __init__(self, message: str = "Usuario no encontrado"):
        self.message = message
        super().__init__(self.message)


class PasswordPolicyException(AuthException):
    """Excepción para contraseñas que no cumplen la política."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        message = "La contraseña no cumple los requisitos: " + ", ".join(errors)
        self.message = message
        super().__init__(self.message)


class RateLimitException(AuthException):
    """Excepción para límite de intentos excedido."""
    def __init__(self, message: str = "Demasiados intentos. Intente más tarde."):
        self.message = message
        super().__init__(self.message)


class TokenExpiredException(AuthException):
    """Excepción para tokens expirados."""
    def __init__(self, message: str = "El token ha expirado"):
        self.message = message
        super().__init__(self.message)


class InvalidTokenException(AuthException):
    """Excepción para tokens inválidos."""
    def __init__(self, message: str = "Token inválido o manipulado"):
        self.message = message
        super().__init__(self.message)


class AuthUser(ABC):
    """
    Clase base abstracta para usuarios autenticables.
    
    Esta clase define la interfaz que deben implementar los modelos de usuario
    para ser compatibles con el sistema de autenticación.
    
    Attributes:
        username (str): Nombre de usuario o identificador único.
        email (str): Correo electrónico del usuario.
        password_hash (str): Hash de la contraseña del usuario.
        is_active (bool): Indica si el usuario está activo.
        is_verified (bool): Indica si el usuario ha verificado su email.
    """
    
    @property
    @abstractmethod
    def username(self) -> str:
        """Obtiene el nombre de usuario o identificador único."""
        pass
    
    @property
    @abstractmethod
    def email(self) -> str:
        """Obtiene el correo electrónico del usuario."""
        pass
    
    @property
    @abstractmethod
    def password_hash(self) -> str:
        """Obtiene el hash de la contraseña del usuario."""
        pass
    
    @property
    @abstractmethod
    def is_active(self) -> bool:
        """Indica si el usuario está activo."""
        pass
    
    @property
    @abstractmethod
    def is_verified(self) -> bool:
        """Indica si el usuario ha verificado su email."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el usuario a un diccionario.
        
        Returns:
            Dict[str, Any]: Diccionario con los datos del usuario.
        """
        pass


class LoginResult:
    """
    Resultado de un intento de login.
    
    Attributes:
        success (bool): Indica si el login fue exitoso.
        access_token (Optional[str]): Token de acceso (si login exitoso).
        refresh_token (Optional[str]): Token de refresco (si login exitoso y habilitado).
        user (Optional[AuthUser]): Usuario autenticado (si login exitoso).
        message (str): Mensaje descriptivo del resultado.
        expires_at (Optional[datetime]): Fecha/hora de expiración del token.
    """
    
    def __init__(
        self,
        success: bool = False,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        user: Optional[AuthUser] = None,
        message: str = "",
        expires_at: Optional[datetime] = None
    ):
        """
        Inicializa un resultado de login.
        
        Args:
            success (bool, optional): Indica si el login fue exitoso. Por defecto False.
            access_token (Optional[str], optional): Token de acceso. Por defecto None.
            refresh_token (Optional[str], optional): Token de refresco. Por defecto None.
            user (Optional[AuthUser], optional): Usuario autenticado. Por defecto None.
            message (str, optional): Mensaje descriptivo. Por defecto "".
            expires_at (Optional[datetime], optional): Fecha/hora de expiración. Por defecto None.
        """
        self.success = success
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user = user
        self.message = message
        self.expires_at = expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el resultado a un diccionario.
        
        Returns:
            Dict[str, Any]: Diccionario con los datos del resultado.
        """
        return {
            "success": self.success,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "user": self.user.to_dict() if self.user else None,
            "message": self.message,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }


class AuthManager(Generic[T]):
    """
    Gestor de autenticación para usuarios.
    
    Esta clase proporciona métodos para autenticar usuarios, verificar tokens,
    registrar nuevos usuarios, etc. Es compatible con diferentes frameworks web.
    
    Attributes:
        user_model (Type[T]): Clase del modelo de usuario.
        get_user_by_username (Callable): Función para obtener usuario por nombre.
        get_user_by_email (Callable): Función para obtener usuario por email.
        save_user (Callable): Función para guardar un usuario.
        update_user (Callable): Función para actualizar un usuario.
    """
    
    def __init__(
        self,
        user_model: Type[T],
        get_user_by_username: Callable[[str], Optional[T]],
        get_user_by_email: Callable[[str], Optional[T]],
        save_user: Optional[Callable[[T], None]] = None,
        update_user: Optional[Callable[[T], None]] = None,
    ):
        """
        Inicializa el gestor de autenticación.
        
        Args:
            user_model (Type[T]): Clase del modelo de usuario.
            get_user_by_username (Callable): Función para obtener un usuario por nombre.
            get_user_by_email (Callable): Función para obtener un usuario por email.
            save_user (Optional[Callable], optional): Función para guardar un usuario. 
                                                    Por defecto None.
            update_user (Optional[Callable], optional): Función para actualizar un usuario.
                                                      Por defecto None.
        """
        self.user_model = user_model
        self.get_user_by_username = get_user_by_username
        self.get_user_by_email = get_user_by_email
        self.save_user = save_user
        self.update_user = update_user
    
    def _check_rate_limit(self, identifier: str) -> None:
        """
        Verifica si un identificador ha superado el límite de intentos.
        
        Args:
            identifier (str): Identificador (usuario, IP, etc).
            
        Raises:
            RateLimitException: Si se ha superado el límite de intentos.
        """
        now = time.time()
        window_start = now - config.RATE_LIMIT_WINDOW_SECONDS
        
        # Inicializar o actualizar timestamps de intentos
        if identifier not in _login_attempts:
            _login_attempts[identifier] = []
        
        # Limpiar intentos antiguos
        _login_attempts[identifier] = [t for t in _login_attempts[identifier] if t > window_start]
        
        # Verificar límite
        if len(_login_attempts[identifier]) >= config.RATE_LIMIT_MAX_ATTEMPTS:
            _logger.warning(f"Rate limit excedido para: {identifier}")
            raise RateLimitException()
        
        # Registrar intento
        _login_attempts[identifier].append(now)
    
    def authenticate(self, username: str, password: str) -> LoginResult:
        """
        Autentica un usuario por sus credenciales.
        
        Args:
            username (str): Nombre de usuario o email.
            password (str): Contraseña en texto plano.
            
        Returns:
            LoginResult: Resultado del intento de login.
            
        Raises:
            RateLimitException: Si se ha superado el límite de intentos.
        """
        try:
            # Verificar límite de intentos
            self._check_rate_limit(username)
            
            # Buscar usuario
            user = self.get_user_by_username(username)
            if not user:
                # Probar con email
                user = self.get_user_by_email(username)
            
            if not user:
                _logger.warning(f"Intento de login con usuario inexistente: {username}")
                return LoginResult(success=False, message="Usuario o contraseña incorrectos")
            
            # Verificar contraseña
            if not verify_password(password, user.password_hash):
                _logger.warning(f"Contraseña incorrecta para usuario: {username}")
                return LoginResult(success=False, message="Usuario o contraseña incorrectos")
            
            # Verificar si el usuario está activo
            if not user.is_active:
                _logger.warning(f"Intento de login con usuario inactivo: {username}")
                return LoginResult(success=False, message="Usuario inactivo")
            
            # Generar tokens
            access_token_data = {
                "sub": user.username,
                "email": user.email,
                "jti": str(uuid.uuid4())
            }
            
            access_token = create_access_token(access_token_data)
            refresh_token = None
            
            if config.ENABLE_REFRESH_TOKENS:
                refresh_token = create_refresh_token(access_token_data)
            
            # Calcular expiración
            expires_at = datetime.utcnow() + config.get_access_token_expires_delta()
            
            _logger.info(f"Login exitoso para usuario: {username}")
            return LoginResult(
                success=True,
                access_token=access_token,
                refresh_token=refresh_token,
                user=user,
                message="Login exitoso",
                expires_at=expires_at
            )
            
        except RateLimitException:
            raise
        except Exception as e:
            _logger.error(f"Error durante autenticación: {e}", exc_info=True)
            return LoginResult(success=False, message=f"Error de autenticación: {str(e)}")
    
    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        **kwargs
    ) -> Union[T, str]:
        """
        Registra un nuevo usuario.
        
        Args:
            username (str): Nombre de usuario.
            email (str): Correo electrónico.
            password (str): Contraseña en texto plano.
            **kwargs: Argumentos adicionales para el modelo de usuario.
            
        Returns:
            Union[T, str]: Usuario creado o mensaje de error.
            
        Raises:
            PasswordPolicyException: Si la contraseña no cumple los requisitos.
            ValueError: Si falta el método save_user o datos obligatorios.
        """
        if not self.save_user:
            raise ValueError("Método save_user no proporcionado")
        
        if not username or not email or not password:
            raise ValueError("Nombre de usuario, email y contraseña son obligatorios")
        
        # Verificar si el usuario ya existe
        existing_user = self.get_user_by_username(username)
        if existing_user:
            _logger.warning(f"Intento de registro con nombre de usuario existente: {username}")
            return f"El nombre de usuario '{username}' ya está en uso"
        
        # Verificar si el email ya existe
        existing_email = self.get_user_by_email(email)
        if existing_email:
            _logger.warning(f"Intento de registro con email existente: {email}")
            return f"El email '{email}' ya está registrado"
        
        # Verificar política de contraseñas
        meets_requirements, errors = password_meets_requirements(password)
        if not meets_requirements:
            _logger.warning(f"Contraseña no cumple requisitos en registro: {username}")
            raise PasswordPolicyException(errors)
        
        # Generar hash de contraseña
        password_hash = hash_password(password)
        
        try:
            # Crear nuevo usuario
            user_data = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "is_active": True,
                "is_verified": False,
                **kwargs
            }
            
            # Crear instancia según el modelo
            user = self.user_model(**user_data)
            
            # Guardar usuario
            self.save_user(user)
            
            _logger.info(f"Usuario registrado correctamente: {username}")
            return user
        except Exception as e:
            _logger.error(f"Error al registrar usuario: {e}", exc_info=True)
            return f"Error al registrar usuario: {str(e)}"
    
    def verify_token(self, token: str) -> Optional[T]:
        """
        Verifica un token y devuelve el usuario asociado.
        
        Args:
            token (str): Token JWT a verificar.
            
        Returns:
            Optional[T]: Usuario asociado al token o None si no es válido.
        """
        try:
            payload = verify_token(token, TOKEN_TYPE_ACCESS)
            
            username = payload.get("sub")
            if not username:
                return None
            
            user = self.get_user_by_username(username)
            if not user or not user.is_active:
                return None
            
            return user
        except Exception as e:
            _logger.error(f"Error al verificar token: {e}")
            return None
    
    def get_user_from_token(self, token: str) -> Optional[T]:
        """
        Obtiene el usuario a partir de un token.
        
        Args:
            token (str): Token JWT.
            
        Returns:
            Optional[T]: Usuario asociado al token o None si no es válido.
            
        Raises:
            InvalidTokenException: Si el token es inválido.
            TokenExpiredException: Si el token ha expirado.
            UserNotFoundException: Si el usuario no existe o no está activo.
        """
        try:
            payload = verify_token(token, TOKEN_TYPE_ACCESS)
            
            username = payload.get("sub")
            if not username:
                raise InvalidTokenException("Token sin identificador de usuario")
            
            user = self.get_user_by_username(username)
            if not user:
                raise UserNotFoundException()
            
            if not user.is_active:
                raise UserNotFoundException("Usuario inactivo")
            
            return user
        except Exception as e:
            _logger.error(f"Error al obtener usuario de token: {e}")
            if "expired" in str(e).lower():
                raise TokenExpiredException()
            raise InvalidTokenException()
    
    def change_password(
        self,
        user: T,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            user (T): Usuario cuya contraseña se cambiará.
            current_password (str): Contraseña actual.
            new_password (str): Nueva contraseña.
            
        Returns:
            bool: True si el cambio fue exitoso, False en caso contrario.
            
        Raises:
            ValueError: Si falta el método update_user.
            InvalidCredentialsException: Si la contraseña actual es incorrecta.
            PasswordPolicyException: Si la nueva contraseña no cumple los requisitos.
        """
        if not self.update_user:
            raise ValueError("Método update_user no proporcionado")
        
        # Verificar contraseña actual
        if not verify_password(current_password, user.password_hash):
            _logger.warning(f"Contraseña actual incorrecta en cambio de contraseña: {user.username}")
            raise InvalidCredentialsException("Contraseña actual incorrecta")
        
        # Verificar política para nueva contraseña
        meets_requirements, errors = password_meets_requirements(new_password)
        if not meets_requirements:
            _logger.warning(f"Nueva contraseña no cumple requisitos: {user.username}")
            raise PasswordPolicyException(errors)
        
        try:
            # Generar nuevo hash
            password_hash = hash_password(new_password)
            
            # Actualizar contraseña
            user.password_hash = password_hash
            self.update_user(user)
            
            _logger.info(f"Contraseña cambiada correctamente: {user.username}")
            return True
        except Exception as e:
            _logger.error(f"Error al cambiar contraseña: {e}", exc_info=True)
            return False


# Funciones de ayuda

def authenticate_user(
    auth_manager: AuthManager[T],
    username: str,
    password: str
) -> LoginResult:
    """
    Autentica un usuario usando un AuthManager.
    
    Args:
        auth_manager (AuthManager[T]): Gestor de autenticación.
        username (str): Nombre de usuario o email.
        password (str): Contraseña en texto plano.
        
    Returns:
        LoginResult: Resultado del intento de login.
    """
    return auth_manager.authenticate(username, password)


def get_current_user(
    auth_manager: AuthManager[T],
    token: str
) -> Optional[T]:
    """
    Obtiene el usuario actual a partir de un token.
    
    Args:
        auth_manager (AuthManager[T]): Gestor de autenticación.
        token (str): Token JWT.
        
    Returns:
        Optional[T]: Usuario o None si el token no es válido.
    """
    return auth_manager.verify_token(token)
