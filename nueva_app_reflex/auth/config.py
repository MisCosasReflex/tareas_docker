"""
Configuración centralizada para el sistema de autenticación.

Este módulo contiene todas las configuraciones necesarias para el sistema de autenticación,
permitiendo una personalización fácil según las necesidades de cada aplicación.

Attributes:
    SECRET_KEY (str): Clave secreta para la generación de tokens JWT.
    ACCESS_TOKEN_EXPIRE_MINUTES (int): Tiempo de expiración para tokens de acceso.
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS (int): Tiempo de expiración para tokens de verificación.
    REFRESH_TOKEN_EXPIRE_DAYS (int): Tiempo de expiración para tokens de refresco.
    PASSWORD_MIN_LENGTH (int): Longitud mínima de contraseñas.
    ALGORITHM (str): Algoritmo utilizado para la firma de tokens JWT.
    EMAIL_TEMPLATES_DIR (str): Directorio para plantillas de correos.
    LOGIN_URL (str): URL para la página de login.
    PASSWORD_RESET_URL (str): URL para la página de reset de contraseña.
    ARGON2_TIME_COST (int): Factor de costo de tiempo para Argon2.
    ARGON2_MEMORY_COST (int): Factor de costo de memoria para Argon2.
    ARGON2_PARALLELISM (int): Factor de paralelismo para Argon2.
    RATE_LIMIT_MAX_ATTEMPTS (int): Máximo de intentos para rate limiting.
    RATE_LIMIT_WINDOW_SECONDS (int): Ventana de tiempo para rate limiting.
"""

from typing import Dict, Any, Optional
import os
from pydantic import BaseModel, SecretStr
from datetime import timedelta
import secrets

class AuthConfig(BaseModel):
    """
    Configuración para el sistema de autenticación usando Pydantic.
    
    Esta clase permite la validación de la configuración y proporciona valores por defecto
    seguros. También permite la carga desde variables de entorno o archivos de configuración.
    """
    # Configuración de seguridad básica
    SECRET_KEY: SecretStr = SecretStr(os.getenv("AUTH_SECRET_KEY", secrets.token_urlsafe(32)))
    ALGORITHM: str = "HS256"
    
    # Tiempos de expiración
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")) 
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = int(os.getenv("EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS", "24"))
    
    # Configuración de contraseñas
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    ARGON2_TIME_COST: int = int(os.getenv("ARGON2_TIME_COST", "2"))
    ARGON2_MEMORY_COST: int = int(os.getenv("ARGON2_MEMORY_COST", "102400"))  # 100 MB
    ARGON2_PARALLELISM: int = int(os.getenv("ARGON2_PARALLELISM", "8"))
    
    # URLs
    LOGIN_URL: str = "/login"
    PASSWORD_RESET_URL: str = "/reset-password"
    
    # Protección contra ataques
    RATE_LIMIT_MAX_ATTEMPTS: int = int(os.getenv("RATE_LIMIT_MAX_ATTEMPTS", "5"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "300"))  # 5 minutos
    
    # Funcionalidades opcionales
    ENABLE_REFRESH_TOKENS: bool = os.getenv("ENABLE_REFRESH_TOKENS", "True").lower() in ('true', '1', 't')
    ENABLE_EMAIL_VERIFICATION: bool = os.getenv("ENABLE_EMAIL_VERIFICATION", "True").lower() in ('true', '1', 't')
    ENABLE_2FA: bool = os.getenv("ENABLE_2FA", "False").lower() in ('true', '1', 't')
    
    def get_access_token_expires_delta(self) -> timedelta:
        """
        Obtiene el tiempo de expiración para tokens de acceso.
        
        Returns:
            timedelta: Objeto timedelta con la duración de expiración.
        """
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    def get_refresh_token_expires_delta(self) -> timedelta:
        """
        Obtiene el tiempo de expiración para tokens de refresco.
        
        Returns:
            timedelta: Objeto timedelta con la duración de expiración.
        """
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
    
    def get_email_verification_token_expires_delta(self) -> timedelta:
        """
        Obtiene el tiempo de expiración para tokens de verificación de email.
        
        Returns:
            timedelta: Objeto timedelta con la duración de expiración.
        """
        return timedelta(hours=self.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    
    def get_secret_key(self) -> str:
        """
        Obtiene la clave secreta para firmar tokens.
        
        Returns:
            str: La clave secreta como cadena de texto.
        """
        return self.SECRET_KEY.get_secret_value()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AuthConfig":
        """
        Crea una instancia de configuración desde un diccionario.
        
        Args:
            config_dict (Dict[str, Any]): Diccionario con valores de configuración.
            
        Returns:
            AuthConfig: Instancia de configuración.
        """
        return cls(**config_dict)
    
    @classmethod
    def from_env(cls) -> "AuthConfig":
        """
        Crea una instancia de configuración desde variables de entorno.
        
        Las variables deben tener el prefijo AUTH_ seguido del nombre de la configuración.
        
        Returns:
            AuthConfig: Instancia de configuración.
        """
        # Cargar configuración desde variables de entorno
        config_dict = {}
        for key, value in os.environ.items():
            if key.startswith("AUTH_"):
                config_key = key[5:]
                if hasattr(cls, config_key):
                    config_dict[config_key] = value
        
        # Combinar con valores por defecto
        return cls(**config_dict)

# Instancia global de configuración con valores por defecto
auth_config = AuthConfig()

def get_auth_config() -> AuthConfig:
    """
    Función para obtener la configuración de autenticación actual.
    
    Returns:
        AuthConfig: La configuración de autenticación.
    """
    return auth_config

def configure_auth(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Configura el sistema de autenticación con valores personalizados.
    
    Args:
        config (Optional[Dict[str, Any]], optional): Diccionario con valores de configuración. 
                                                   Si es None, se utilizan variables de entorno.
    """
    global auth_config
    if config is not None:
        auth_config = AuthConfig.from_dict(config)
    else:
        auth_config = AuthConfig.from_env()
