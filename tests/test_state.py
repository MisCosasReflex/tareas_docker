"""
Tests unitarios para la lógica de registro y consulta de usuarios, sin depender de Reflex State.

Este archivo contiene pruebas para:
- Lógica pura de registro y consulta de usuarios usando la base de datos
- Validación de restricciones y manejo de errores

Uso:
    Ejecutar con pytest para validar la lógica de negocio independiente del framework Reflex.
"""
import pytest
from typing import Optional
from nueva_app_reflex.db.schemas import UsuarioCreate
from nueva_app_reflex.db.models import Usuario
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
import hashlib

@pytest.fixture(scope="function")
def db_session():
    """
    Crea una base de datos SQLite en memoria para pruebas y retorna una sesión.

    Returns:
        Session: Sesión de SQLAlchemy para pruebas.
    """
    engine_test = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionTest = sessionmaker(bind=engine_test)
    Usuario.metadata.create_all(engine_test)
    session = SessionTest()
    yield session
    session.close()

def registrar_usuario(db, nombre: str, email: str, password: str, es_admin: bool = False) -> Optional[str]:
    """
    Lógica pura de registro de usuario, sin Reflex State.

    Valida los datos, genera el hash de la contraseña y guarda el usuario en la base de datos.
    Maneja errores de validación y de integridad (usuarios duplicados).

    Args:
        db (Session): Sesión de base de datos.
        nombre (str): Nombre de usuario.
        email (str): Correo electrónico del usuario.
        password (str): Contraseña en texto plano.
        es_admin (bool, opcional): Indica si el usuario es administrador. Por defecto False.

    Returns:
        str | None: Mensaje de éxito o error.
    """
    try:
        usuario = UsuarioCreate(
            nombre=nombre,
            email=email,
            password=password,
            es_admin=es_admin,
        )
    except ValidationError as e:
        return f"Error de validación: {e}"
    try:
        password_hash = hashlib.sha256(usuario.password.encode()).hexdigest()
        nuevo_usuario = Usuario(
            nombre=usuario.nombre,
            email=usuario.email,
            password_hash=password_hash,
            es_admin=usuario.es_admin,
        )
        db.add(nuevo_usuario)
        db.commit()
        return f"Usuario '{usuario.nombre}' creado con éxito."
    except IntegrityError:
        db.rollback()
        return f"El usuario '{usuario.nombre}' o el email '{usuario.email}' ya existen."
    except Exception as e:
        db.rollback()
        return f"Error al crear usuario: {e}"

def consultar_usuarios(db):
    """
    Lógica pura para consultar todos los usuarios.

    Recupera la lista de usuarios y retorna un mensaje.

    Args:
        db (Session): Sesión de base de datos.

    Returns:
        tuple: (lista de usuarios, mensaje)
    """
    try:
        usuarios = db.query(Usuario).all()
        if usuarios:
            lista = [
                {"nombre": u.nombre, "email": u.email, "es_admin": u.es_admin}
                for u in usuarios
            ]
            return lista, f"{len(usuarios)} usuario(s) encontrados."
        else:
            return [], "No hay usuarios registrados."
    except Exception as e:
        return [], f"Error al consultar usuarios: {e}"

# TESTS UNITARIOS

def test_registrar_usuario_exitoso(db_session):
    """
    Prueba que se registre un usuario correctamente.

    Valida que el usuario se almacene y recupere de la base de datos.
    """
    msg = registrar_usuario(db_session, "Juan", "juan@ejemplo.com", "passwordseguro", False)
    assert "creado con éxito" in msg
    usuarios = db_session.query(Usuario).all()
    assert len(usuarios) == 1
    assert usuarios[0].nombre == "Juan"
    assert usuarios[0].email == "juan@ejemplo.com"
    assert usuarios[0].es_admin is False

def test_registrar_usuario_validacion(db_session):
    """
    Prueba que la validación de datos falle con nombre corto o password corta.

    Verifica que no se registre ningún usuario inválido.
    """
    msg = registrar_usuario(db_session, "Jo", "jo@ejemplo.com", "pass", False)
    assert "Error de validación" in msg
    usuarios = db_session.query(Usuario).all()
    assert len(usuarios) == 0

def test_registrar_usuario_duplicado(db_session):
    """
    Prueba que no se permita registrar dos usuarios con el mismo email o nombre.

    Valida que sólo un usuario quede registrado ante duplicados.
    """
    msg1 = registrar_usuario(db_session, "Ana", "ana@ejemplo.com", "clave1234", False)
    msg2 = registrar_usuario(db_session, "Ana", "ana@ejemplo.com", "clave1234", False)
    assert "creado con éxito" in msg1
    assert "ya existen" in msg2
    usuarios = db_session.query(Usuario).all()
    assert len(usuarios) == 1

def test_consultar_usuarios_vacio(db_session):
    """
    Prueba que consultar usuarios con la base vacía retorna el mensaje adecuado.

    Verifica que la lista esté vacía y el mensaje sea el esperado.
    """
    lista, msg = consultar_usuarios(db_session)
    assert lista == []
    assert "No hay usuarios" in msg

def test_consultar_usuarios_con_usuarios(db_session):
    """
    Prueba que consultar usuarios retorna la lista y mensaje correcto.

    Verifica que los datos de los usuarios sean correctos en la consulta.
    """
    registrar_usuario(db_session, "Luis", "luis@ejemplo.com", "clave1234", True)
    lista, msg = consultar_usuarios(db_session)
    assert len(lista) == 1
    assert lista[0]["nombre"] == "Luis"
    assert lista[0]["es_admin"] is True
    assert "1 usuario(s) encontrados" in msg
