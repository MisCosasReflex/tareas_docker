"""
Tests unitarios para los modelos de base de datos y schemas de usuario en Reflex.

Este archivo contiene pruebas para:
- Validación de esquemas Pydantic para usuario
- Persistencia y recuperación de usuarios y tareas en la base de datos

Uso:
    Ejecutar con pytest para validar el correcto funcionamiento de los modelos y schemas.
"""
import pytest
from nueva_app_reflex.db.models import Usuario, Tarea
from nueva_app_reflex.db.schemas import UsuarioCreate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Crea una base de datos SQLite en memoria para pruebas unitarias y retorna una sesión.

    ¿Por qué se usa una base en memoria?
    -----------------------------------
    Usar `sqlite:///:memory:` permite que cada prueba tenga una base de datos limpia y temporal,
    evitando efectos colaterales entre pruebas y garantizando aislamiento.

    Returns:
        Session: Sesión de SQLAlchemy lista para usar en pruebas.
    """
    engine_test = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionTest = sessionmaker(bind=engine_test)
    # Crear las tablas necesarias en la base de datos de prueba
    Usuario.metadata.create_all(engine_test)
    Tarea.metadata.create_all(engine_test)
    session = SessionTest()
    yield session  # Devuelve la sesión para usarla en la prueba
    session.close()  # Cierra la sesión al finalizar la prueba


def test_usuario_create_schema_valido() -> None:
    """
    Prueba que el schema Pydantic de usuario acepte datos válidos.

    ¿Por qué es importante?
    ----------------------
    Permite validar que el esquema Pydantic funciona correctamente y acepta datos válidos
    para la creación de usuarios. Así se previenen errores de validación inesperados.
    """
    usuario = UsuarioCreate(nombre="Pedro", email="pedro@correo.com", password="clave123", es_admin=True)
    assert usuario.nombre == "Pedro"
    assert usuario.email == "pedro@correo.com"
    assert usuario.password == "clave123"
    assert usuario.es_admin is True


def test_usuario_create_schema_invalido() -> None:
    """
    Prueba que el schema Pydantic rechace datos inválidos.

    ¿Por qué es importante?
    ----------------------
    Ayuda a asegurar que los datos incorrectos (nombre demasiado corto, email inválido, password corta)
    no sean aceptados y se levante una excepción de validación.
    """
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        UsuarioCreate(nombre="A", email="noemail", password="123", es_admin=False)


def test_modelo_usuario_persistencia(db_session: Session) -> None:
    """
    Prueba que se pueda guardar y recuperar un usuario en la base de datos.

    ¿Por qué es importante?
    ----------------------
    Garantiza que la lógica de persistencia funciona correctamente:
    - Se puede guardar un usuario en la base de datos.
    - Se puede recuperar el mismo usuario y sus atributos coinciden con los ingresados.
    """
    usuario = Usuario(nombre="Maria", email="maria@correo.com", password_hash="hash123", es_admin=False)
    db_session.add(usuario)
    db_session.commit()
    usuario_db = db_session.query(Usuario).filter_by(nombre="Maria").first()
    assert usuario_db is not None
    assert usuario_db.email == "maria@correo.com"
    assert usuario_db.password_hash == "hash123"
    assert usuario_db.es_admin is False


def test_modelo_tarea_persistencia(db_session: Session) -> None:
    """
    Prueba que se pueda guardar y recuperar una tarea asociada a un usuario.

    ¿Por qué es importante?
    ----------------------
    Verifica la integridad de la relación entre usuario y tarea.
    """
    usuario = Usuario(nombre="Carlos", email="carlos@correo.com", password_hash="hash", es_admin=False)
    db_session.add(usuario)
    db_session.commit()
    tarea = Tarea(descripcion="Probar Reflex", completada=False, usuario_id=usuario.id)
    db_session.add(tarea)
    db_session.commit()
    tarea_db = db_session.query(Tarea).filter_by(descripcion="Probar Reflex").first()
    assert tarea_db is not None
    assert tarea_db.descripcion == "Probar Reflex"
    assert tarea_db.usuario_id == usuario.id
    assert tarea_db.completada is False