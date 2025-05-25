"""
Módulo para la gestión segura de contraseñas.

Este módulo proporciona funciones para el hasheo y verificación de contraseñas
utilizando el algoritmo Argon2, ganador de la competición de hasheo de contraseñas.
Incluye protección contra timing attacks y configuración personalizable.

Functions:
    hash_password: Genera un hash seguro para una contraseña.
    verify_password: Verifica si una contraseña coincide con un hash.
    password_meets_requirements: Valida si una contraseña cumple con los requisitos de seguridad.
    generate_strong_password: Genera una contraseña fuerte aleatoria.
"""

from typing import Dict, Tuple, Optional, List
import secrets
import string
import time
import re

# Importar dependencias Argon2
try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
except ImportError:
    raise ImportError(
        "El módulo argon2-cffi no está instalado. Por favor, instálalo con 'pip install argon2-cffi'"
    )

from ..config import get_auth_config

# Obtener configuración
config = get_auth_config()

# Inicializar hasher con configuración
_password_hasher = PasswordHasher(
    time_cost=config.ARGON2_TIME_COST,
    memory_cost=config.ARGON2_MEMORY_COST,
    parallelism=config.ARGON2_PARALLELISM,
)


def hash_password(password: str) -> str:
    """
    Genera un hash seguro para una contraseña usando Argon2.

    Args:
        password (str): La contraseña en texto plano a hashear.

    Returns:
        str: El hash generado, que incluye la sal y los parámetros.

    Example:
        >>> hash_password("mi_contraseña_segura")
        '$argon2id$v=19$m=102400,t=2,p=8$...'
    """
    if not password:
        raise ValueError("La contraseña no puede estar vacía")
    
    return _password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con un hash, con protección contra timing attacks.

    Args:
        plain_password (str): La contraseña en texto plano a verificar.
        hashed_password (str): El hash con el que comparar.

    Returns:
        bool: True si la contraseña es correcta, False en caso contrario.

    Example:
        >>> verify_password("mi_contraseña_segura", hash_almacenado)
        True
    """
    if not plain_password or not hashed_password:
        return False
    
    try:
        # Argon2 ya implementa protección contra timing attacks
        _password_hasher.verify(hashed_password, plain_password)
        
        # Verificar si el hash necesita rehash (por actualización de parámetros)
        if _password_hasher.check_needs_rehash(hashed_password):
            # El sistema debería actualizar el hash en este punto
            # (implementar en el código que llama a esta función)
            pass
            
        return True
    except (VerifyMismatchError, VerificationError, InvalidHash):
        # Asegurar tiempo constante de respuesta para evitar timing attacks
        # Aunque argon2 ya tiene protección, añadimos una capa adicional
        time.sleep(secrets.randbelow(10) / 1000)  # 0-10ms aleatorio
        return False


def password_meets_requirements(password: str) -> Tuple[bool, List[str]]:
    """
    Valida si una contraseña cumple con los requisitos de seguridad.

    Args:
        password (str): La contraseña a validar.

    Returns:
        Tuple[bool, List[str]]: Una tupla con un booleano indicando si cumple los requisitos
                              y una lista de mensajes de error (vacía si todo está bien).

    Example:
        >>> password_meets_requirements("abc123")
        (False, ['La contraseña debe tener al menos 8 caracteres',
                'La contraseña debe contener al menos una letra mayúscula'])
    """
    errors = []
    
    # Verificar longitud mínima
    if len(password) < config.PASSWORD_MIN_LENGTH:
        errors.append(f"La contraseña debe tener al menos {config.PASSWORD_MIN_LENGTH} caracteres")
    
    # Verificar complejidad
    if not re.search(r"[A-Z]", password):
        errors.append("La contraseña debe contener al menos una letra mayúscula")
    
    if not re.search(r"[a-z]", password):
        errors.append("La contraseña debe contener al menos una letra minúscula")
    
    if not re.search(r"[0-9]", password):
        errors.append("La contraseña debe contener al menos un número")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("La contraseña debe contener al menos un carácter especial")
    
    # Verificar que no sea una contraseña común
    common_passwords = {"password", "123456", "qwerty", "admin", "welcome"}
    if password.lower() in common_passwords:
        errors.append("La contraseña es demasiado común")
    
    return (len(errors) == 0, errors)


def generate_strong_password(length: int = 16) -> str:
    """
    Genera una contraseña fuerte aleatoria.

    Args:
        length (int, optional): Longitud de la contraseña. Por defecto 16.

    Returns:
        str: Contraseña aleatoria segura.

    Example:
        >>> generate_strong_password()
        'X7@pK2!fD9sL5#Rt'
    """
    if length < config.PASSWORD_MIN_LENGTH:
        length = config.PASSWORD_MIN_LENGTH
    
    # Asegurar que incluye todos los tipos de caracteres necesarios
    letters_upper = string.ascii_uppercase
    letters_lower = string.ascii_lowercase
    digits = string.digits
    special_chars = "!@#$%^&*(),.?:{}|<>"
    
    # Generar al menos uno de cada tipo
    password = [
        secrets.choice(letters_upper),
        secrets.choice(letters_lower),
        secrets.choice(digits),
        secrets.choice(special_chars)
    ]
    
    # Completar con caracteres aleatorios
    all_chars = letters_upper + letters_lower + digits + special_chars
    password.extend(secrets.choice(all_chars) for _ in range(length - 4))
    
    # Mezclar la contraseña
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)
