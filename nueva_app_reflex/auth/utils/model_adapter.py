"""
Utilidades para adaptar modelos existentes al sistema de autenticación.

Este módulo proporciona funciones y clases para adaptar modelos existentes
al sistema de autenticación, creando wrappers que implementan la interfaz AuthUser.

Classes:
    SQLAlchemyUserAdapter: Adaptador para modelos SQLAlchemy.
"""

from typing import Dict, Optional, Any, Type, cast
from ..core.auth import AuthUser

class SQLAlchemyUserAdapter(AuthUser):
    """
    Adaptador para modelos SQLAlchemy de usuario.
    
    Esta clase envuelve un modelo SQLAlchemy existente y lo adapta
    a la interfaz AuthUser requerida por el sistema de autenticación.
    
    Attributes:
        _user: Modelo SQLAlchemy de usuario.
        _username_field (str): Nombre del campo que contiene el username.
        _email_field (str): Nombre del campo que contiene el email.
        _password_field (str): Nombre del campo que contiene el hash de contraseña.
        _active_field (str): Nombre del campo que indica si el usuario está activo.
        _verified_field (str): Nombre del campo que indica si el usuario está verificado.
    """
    
    def __init__(
        self,
        user,
        username_field: str = "nombre",
        email_field: str = "email",
        password_field: str = "password_hash",
        active_field: str = "is_active",
        verified_field: str = "is_verified"
    ):
        """
        Inicializa el adaptador.
        
        Args:
            user: Modelo SQLAlchemy de usuario.
            username_field (str, optional): Campo de username. Por defecto "nombre".
            email_field (str, optional): Campo de email. Por defecto "email".
            password_field (str, optional): Campo de hash de contraseña. Por defecto "password_hash".
            active_field (str, optional): Campo de usuario activo. Por defecto "is_active".
            verified_field (str, optional): Campo de usuario verificado. Por defecto "is_verified".
        """
        self._user = user
        self._username_field = username_field
        self._email_field = email_field
        self._password_field = password_field
        self._active_field = active_field
        self._verified_field = verified_field
    
    @property
    def username(self) -> str:
        return getattr(self._user, self._username_field)
    
    @property
    def email(self) -> str:
        return getattr(self._user, self._email_field)
    
    @property
    def password_hash(self) -> str:
        return getattr(self._user, self._password_field)
    
    @password_hash.setter
    def password_hash(self, value: str) -> None:
        """
        Establece el hash de la contraseña.
        
        Args:
            value (str): Nuevo hash de contraseña.
        """
        setattr(self._user, self._password_field, value)
    
    @property
    def is_active(self) -> bool:
        # Si el campo no existe, asumir que está activo
        if not hasattr(self._user, self._active_field):
            return True
        return bool(getattr(self._user, self._active_field))
    
    @property
    def is_verified(self) -> bool:
        # Si el campo no existe, asumir que no está verificado
        if not hasattr(self._user, self._verified_field):
            return False
        return bool(getattr(self._user, self._verified_field))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el usuario a un diccionario.
        
        Returns:
            Dict[str, Any]: Diccionario con los datos del usuario.
        """
        # Hacer un diccionario con atributos básicos
        result = {
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified
        }
        
        # Añadir otros campos que puedan existir
        for key in ["id", "nombre", "is_admin", "es_admin"]:
            if hasattr(self._user, key):
                result[key] = getattr(self._user, key)
        
        return result
    
    @property
    def user(self):
        """
        Devuelve el modelo de usuario original.
        
        Returns:
            El modelo SQLAlchemy de usuario.
        """
        return self._user


def adapt_usuario_model(usuario):
    """
    Crea un adaptador para el modelo Usuario existente.
    
    Args:
        usuario: Instancia del modelo Usuario.
        
    Returns:
        SQLAlchemyUserAdapter: Adaptador que implementa AuthUser.
    """
    return SQLAlchemyUserAdapter(
        usuario,
        username_field="nombre",
        email_field="email",
        password_field="password_hash",
        # Estos campos no existen en el modelo actual, se usarán valores por defecto
        active_field="is_active", 
        verified_field="is_verified"
    )
