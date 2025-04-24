"""
Modelos de base de datos para la aplicación Reflex.
Define las tablas Usuario y Tarea, y sus relaciones.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Usuario(Base):
    """
    Modelo de usuario del sistema.
    Representa a un usuario que puede tener varias tareas asociadas.
    Incluye autenticación y roles (administrador o no).
    """
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False, doc="Hash seguro de la contraseña del usuario.")
    es_admin = Column(Boolean, default=False, nullable=False, doc="Indica si el usuario es administrador.")
    tareas = relationship("Tarea", back_populates="usuario")

class Tarea(Base):
    """
    Modelo de tarea por hacer.
    Cada tarea pertenece a un usuario y tiene un estado de completada.
    """
    __tablename__ = "tareas"
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String, nullable=False)
    completada = Column(Boolean, default=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="tareas")
