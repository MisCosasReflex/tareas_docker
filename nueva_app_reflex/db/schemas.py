"""
Schemas Pydantic para validación de datos de usuario.

Este módulo define los esquemas de validación de datos de usuario para la creación de nuevos registros
usando Pydantic. Permite asegurar restricciones de formato y longitud en los datos recibidos.

Clases:
    - UsuarioCreate: Esquema para crear un usuario nuevo.
"""
from pydantic import BaseModel, constr, EmailStr

class UsuarioCreate(BaseModel):
    """
    Esquema de validación para la creación de un usuario nuevo.

    Atributos:
        nombre (str): Nombre del usuario (mínimo 3, máximo 50 caracteres).
        email (EmailStr): Correo electrónico válido.
        password (str): Contraseña (mínimo 6, máximo 128 caracteres).
        es_admin (bool): Indica si el usuario es administrador. Por defecto False.
    """
    nombre: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6, max_length=128)
    es_admin: bool = False

    class Config:
        """
        Configuración interna de Pydantic para permitir la creación desde atributos ORM.
        """
        from_attributes = True
