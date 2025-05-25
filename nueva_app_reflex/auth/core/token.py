"""
Módulo para la gestión de tokens JWT de autenticación.

Este módulo proporciona funciones para crear y verificar tokens JWT (JSON Web Tokens)
utilizados en autenticación. Soporta diferentes tipos de tokens como acceso,
refresco y verificación de email.

Functions:
    create_access_token: Crea un token JWT de acceso.
    create_refresh_token: Crea un token JWT de refresco.
    create_email_verification_token: Crea un token JWT para verificación de email.
    verify_token: Verifica y decodifica un token JWT.
    get_token_data: Obtiene los datos decodificados de un token JWT.
"""

from typing import Dict, Optional, Any, Union
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import PyJWTError, InvalidTokenError, ExpiredSignatureError

from ..config import get_auth_config

# Obtener configuración
config = get_auth_config()

# Definir tipos de tokens
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"
TOKEN_TYPE_EMAIL_VERIFICATION = "email_verification"
TOKEN_TYPE_PASSWORD_RESET = "password_reset"


def create_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None,
    token_type: str = TOKEN_TYPE_ACCESS
) -> str:
    """
    Crea un token JWT con los datos proporcionados.

    Args:
        data (Dict[str, Any]): Datos a incluir en el token.
        expires_delta (Optional[timedelta], optional): Tiempo de expiración.
            Si es None, se utiliza el predeterminado según el tipo de token.
        token_type (str, optional): Tipo de token (acceso, refresco, etc.).
            Por defecto TOKEN_TYPE_ACCESS.

    Returns:
        str: Token JWT generado.

    Example:
        >>> create_token({"sub": "usuario@ejemplo.com"}, timedelta(minutes=30))
        'eyJhbGciOiJIUzI1NiIsInR5...'
    """
    to_encode = data.copy()
    
    # Establecer tiempo de expiración según el tipo si no se proporcionó
    if expires_delta is None:
        if token_type == TOKEN_TYPE_ACCESS:
            expires_delta = config.get_access_token_expires_delta()
        elif token_type == TOKEN_TYPE_REFRESH:
            expires_delta = config.get_refresh_token_expires_delta()
        elif token_type == TOKEN_TYPE_EMAIL_VERIFICATION:
            expires_delta = config.get_email_verification_token_expires_delta()
        elif token_type == TOKEN_TYPE_PASSWORD_RESET:
            # Por defecto 24 horas para reseteo de contraseña
            expires_delta = timedelta(hours=24)
        else:
            # Valor predeterminado para otros tipos
            expires_delta = timedelta(minutes=15)
    
    # Añadir campos estándar
    expire = datetime.utcnow() + expires_delta
    to_encode.update({
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "type": token_type
    })
    
    # Generar token
    encoded_jwt = jwt.encode(
        to_encode, 
        config.get_secret_key(), 
        algorithm=config.ALGORITHM
    )
    
    return encoded_jwt


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.

    Args:
        data (Dict[str, Any]): Datos a incluir en el token.
        expires_delta (Optional[timedelta], optional): Tiempo de expiración.
            Si es None, se utiliza el predeterminado.

    Returns:
        str: Token JWT de acceso.

    Example:
        >>> create_access_token({"sub": "usuario@ejemplo.com"})
        'eyJhbGciOiJIUzI1NiIsInR5...'
    """
    return create_token(data, expires_delta, TOKEN_TYPE_ACCESS)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de refresco.

    Args:
        data (Dict[str, Any]): Datos a incluir en el token.
        expires_delta (Optional[timedelta], optional): Tiempo de expiración.
            Si es None, se utiliza el predeterminado.

    Returns:
        str: Token JWT de refresco.

    Example:
        >>> create_refresh_token({"sub": "usuario@ejemplo.com"})
        'eyJhbGciOiJIUzI1NiIsInR5...'
    """
    return create_token(data, expires_delta, TOKEN_TYPE_REFRESH)


def create_email_verification_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT para verificación de email.

    Args:
        data (Dict[str, Any]): Datos a incluir en el token.
        expires_delta (Optional[timedelta], optional): Tiempo de expiración.
            Si es None, se utiliza el predeterminado.

    Returns:
        str: Token JWT de verificación de email.

    Example:
        >>> create_email_verification_token({"sub": "usuario@ejemplo.com"})
        'eyJhbGciOiJIUzI1NiIsInR5...'
    """
    return create_token(data, expires_delta, TOKEN_TYPE_EMAIL_VERIFICATION)


def create_password_reset_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT para el reseteo de contraseña.

    Args:
        data (Dict[str, Any]): Datos a incluir en el token.
        expires_delta (Optional[timedelta], optional): Tiempo de expiración.
            Si es None, se utiliza el predeterminado.

    Returns:
        str: Token JWT de reseteo de contraseña.

    Example:
        >>> create_password_reset_token({"sub": "usuario@ejemplo.com"})
        'eyJhbGciOiJIUzI1NiIsInR5...'
    """
    return create_token(data, expires_delta, TOKEN_TYPE_PASSWORD_RESET)


def verify_token(
    token: str, 
    expected_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verifica y decodifica un token JWT.

    Args:
        token (str): Token JWT a verificar.
        expected_type (Optional[str], optional): Tipo de token esperado.
            Si es None, no se valida el tipo.

    Returns:
        Dict[str, Any]: Datos decodificados del token.

    Raises:
        jwt.InvalidTokenError: Si el token no es válido.
        jwt.ExpiredSignatureError: Si el token ha expirado.
        ValueError: Si el tipo del token no coincide con el esperado.

    Example:
        >>> try:
        ...     payload = verify_token(token, TOKEN_TYPE_ACCESS)
        ... except (InvalidTokenError, ExpiredSignatureError) as e:
        ...     print(f"Error: {e}")
        ... else:
        ...     print(f"Token válido: {payload}")
    """
    try:
        # Decodificar token
        payload = jwt.decode(
            token, 
            config.get_secret_key(), 
            algorithms=[config.ALGORITHM]
        )
        
        # Verificar tipo si se especificó
        if expected_type and payload.get("type") != expected_type:
            raise ValueError(f"Tipo de token incorrecto: {payload.get('type')}, esperado: {expected_type}")
        
        return payload
    except ExpiredSignatureError:
        raise ExpiredSignatureError("El token ha expirado")
    except InvalidTokenError:
        raise InvalidTokenError("Token inválido")


def get_token_data(token: str, expected_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos decodificados de un token JWT si es válido.

    Args:
        token (str): Token JWT a decodificar.
        expected_type (Optional[str], optional): Tipo de token esperado.
            Si es None, no se valida el tipo.

    Returns:
        Optional[Dict[str, Any]]: Datos decodificados del token o None si no es válido.

    Example:
        >>> data = get_token_data(token)
        >>> if data:
        ...     print(f"Usuario: {data.get('sub')}")
        ... else:
        ...     print("Token inválido")
    """
    try:
        return verify_token(token, expected_type)
    except (PyJWTError, ValueError):
        return None
