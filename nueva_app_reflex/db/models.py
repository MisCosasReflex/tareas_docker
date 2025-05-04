"""
Modelos de base de datos para la aplicación Reflex.

Este módulo define las clases ORM para la gestión de usuarios y tareas.
Incluye la definición de las tablas, sus relaciones y los campos principales.

Clases:
    - Usuario: Modelo de usuario del sistema.
    - Tarea: Modelo de tarea asociada a un usuario.
"""

from enum import unique
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Usuario(Base):
    """
    Modelo de usuario del sistema.

    Representa a un usuario registrado, que puede tener varias tareas asociadas.
    Incluye autenticación y roles (administrador o no).

    Atributos:
        id (int): Identificador único del usuario (PK).
        nombre (str): Nombre de usuario, único.
        email (str): Correo electrónico, único.
        password_hash (str): Hash seguro de la contraseña.
        es_admin (bool): Indica si el usuario es administrador.
        tareas (list): Lista de tareas asociadas.
    """
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False, doc="Dirección de correo electrónico del usuario.")
    password_hash = Column(String, nullable=False, doc="Hash seguro de la contraseña del usuario.")
    es_admin = Column(Boolean, default=False, nullable=False, doc="Indica si el usuario es administrador.")
    tareas = relationship("Tarea", back_populates="usuario")

class Tarea(Base):
    """
    Modelo de tarea por hacer.

    Cada tarea pertenece a un usuario y tiene un estado de completada.

    Atributos:
        id (int): Identificador único de la tarea (PK).
        descripcion (str): Descripción de la tarea.
        completada (bool): Estado de la tarea (completada o no).
        usuario_id (int): ID del usuario propietario.
        usuario (Usuario): Relación con el usuario propietario.
    """
    __tablename__ = "tareas"
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String, nullable=False)
    completada = Column(Boolean, default=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="tareas")
