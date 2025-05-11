from ..db.database import SessionLocal
from ..db.schemas import UsuarioCreate
from ..db.models import Usuario
from sqlalchemy.exc import IntegrityError
import hashlib
from pydantic import ValidationError
from typing import Optional
from ..utils.logger import get_logger

# Inicializar el logger para este módulo
_logger = get_logger(__name__)

def servicio_registrar_usuario(nombre: str, email: str, password: str, es_admin: bool = False) -> str:
    """
    Registra un nuevo usuario en la base de datos.

    Valida los datos usando Pydantic, genera el hash de la contraseña y guarda el usuario en la base de datos.
    Maneja errores de validación y de integridad (usuarios duplicados).

    Args:
        nombre (str): Nombre de usuario.
        email (str): Correo electrónico del usuario.
        password (str): Contraseña en texto plano.
        es_admin (bool, opcional): Indica si el usuario es administrador. Por defecto False.
        
    Returns:
        str: Mensaje de éxito o error tras el registro.
    """
    try:
        usuario: UsuarioCreate = UsuarioCreate(
            nombre=nombre,
            email=email,
            password=password,
            es_admin=es_admin,
        )
        db = SessionLocal()
        try:
            password_hash: str = hashlib.sha256(usuario.password.encode()).hexdigest()
            nuevo_usuario: Usuario = Usuario(
                nombre=usuario.nombre,
                email=usuario.email,
                password_hash=password_hash,
                es_admin=usuario.es_admin,
            )
            db.add(nuevo_usuario)
            db.commit()
            _logger.debug(f"Usuario guardado: {usuario.nombre}, {usuario.email}, admin={usuario.es_admin}")
            _logger.info(f"Usuario '{usuario.nombre}' creado con éxito")
            return f"Usuario '{usuario.nombre}' creado con éxito."
        except IntegrityError:
            db.rollback()
            _logger.warning(f"Intento de crear usuario duplicado: {usuario.nombre}, {usuario.email}")
            return f"El usuario '{usuario.nombre}' o el email '{usuario.email}' ya existen."
        except Exception as e:
            db.rollback()
            _logger.error(f"Error al crear usuario: {e}", exc_info=True)
            return f"Error al crear usuario: {e}"
        finally:
            db.close()
    except ValidationError as e:
        _logger.error(f"Error de validación: {e}")
        return f"Error de validación: {e}"
    except Exception as e:
        _logger.error(f"Error al crear usuario: {e}", exc_info=True)
        return f"Error al crear usuario: {e}"

def servicio_consultar_usuarios() -> tuple[list[dict], str]:
    """
    Consulta todos los usuarios de la base de datos.

    Recupera la lista de usuarios registrados en la base de datos y los devuelve
    en formato de lista de diccionarios junto con un mensaje de estado.

    Returns:
        tuple[list[dict], str]: Una tupla que contiene:
            - lista_usuarios: Lista de diccionarios con información de los usuarios
            - mensaje: Mensaje de estado indicando el resultado de la operación
    """
    usuarios_lista = []
    mensaje_usuario = ""
    try:
        db = SessionLocal()
        usuarios: list[Usuario] = db.query(Usuario).all()
        _logger.debug(f"Usuarios consultados: {usuarios}")
        if usuarios:
            usuarios_lista = [
                {"nombre": u.nombre, "email": u.email, "es_admin": u.es_admin}
                for u in usuarios
            ]
            mensaje_usuario = f"{len(usuarios)} usuario(s) encontrados."
            _logger.info(f"Consulta exitosa: {len(usuarios)} usuario(s) encontrados")
        else:
            mensaje_usuario = "No hay usuarios registrados."
            _logger.info("Consulta sin resultados: no hay usuarios registrados")
    except Exception as e:
        _logger.error(f"Error al consultar usuarios: {e}", exc_info=True)
        mensaje_usuario = f"Error al consultar usuarios: {e}"
    finally:
        db.close()
    return usuarios_lista, mensaje_usuario


def servicio_filtrar_usuario(nombre: str) -> tuple[list[dict], str]:
    """
    Busca un usuario por nombre exacto en la base de datos.

    Realiza una búsqueda de un usuario específico por su nombre exacto y devuelve
    la información del usuario encontrado en formato de lista de diccionarios.

    Args:
        nombre (str): Nombre exacto del usuario a buscar.

    Returns:
        tuple[list[dict], str]: Una tupla que contiene:
            - lista_usuarios: Lista con la información del usuario encontrado (o vacía si no se encuentra)
            - mensaje: Mensaje de estado indicando el resultado de la operación
    """
    usuarios_lista = []
    mensaje_usuario = ""
    try:
        _logger.debug(f"Iniciando búsqueda de usuario por nombre: {nombre}")
        db = SessionLocal()
        usuario_encontrado: Optional[Usuario] = db.query(Usuario).filter(Usuario.nombre == nombre).first()
        if usuario_encontrado:
            usuarios_lista = [
                {"nombre": usuario_encontrado.nombre,
                    "email": usuario_encontrado.email,
                    "es_admin": usuario_encontrado.es_admin}
            ]
            mensaje_usuario = f"Usuario '{usuario_encontrado.nombre}' encontrado."
            _logger.info(f"Usuario encontrado en filtrado: {usuario_encontrado.nombre}")
        else:
            mensaje_usuario = "No se encontro el usuario."
            _logger.info(f"Filtrado sin resultados para: {nombre}")
    except Exception as e:
        _logger.error(f"Error al filtrar usuario '{nombre}': {e}", exc_info=True)
        mensaje_usuario = f"Error al consultar usuarios: {e}"
    finally:
        db.close()
    return usuarios_lista, mensaje_usuario


def servicio_eliminar_usuario(nombre:str) -> None:
    # servicio_filtrar_usuario devuelve una tupla (lista_usuarios, mensaje)
    usuarios_lista, _ = servicio_filtrar_usuario(nombre)
    
    # Verificar si la lista de usuarios tiene elementos
    if usuarios_lista:
        db = SessionLocal()
        try:
            # Verificar explícitamente si el usuario existe
            usuario_eliminado = db.query(Usuario).filter(Usuario.nombre == nombre).first()
            if usuario_eliminado is not None:
                db.delete(usuario_eliminado)
                db.commit()
                _logger.info(f"Usuario eliminado: {nombre}")
            else:
                _logger.warning(f"No se encontró el usuario '{nombre}' para eliminar")
        except Exception as e:
            db.rollback()
            _logger.error(f"Error al eliminar usuario '{nombre}': {e}", exc_info=True)
        finally:
            db.close()

