from ..db.database import SessionLocal
from ..db.schemas import UsuarioCreate
from ..db.models import Usuario
from sqlalchemy.exc import IntegrityError
import hashlib
from pydantic import ValidationError
from typing import Optional

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
            print(f"[DEBUG] Usuario guardado: {usuario.nombre}, {usuario.email}, admin={usuario.es_admin}")
            return f"Usuario '{usuario.nombre}' creado con éxito."
        except IntegrityError:
            db.rollback()
            return f"El usuario '{usuario.nombre}' o el email '{usuario.email}' ya existen."
        except Exception as e:
            db.rollback()
            return f"Error al crear usuario: {e}"
        finally:
            db.close()
    except ValidationError as e:
        return f"Error de validación: {e}"
    except Exception as e:
        return f"Error al crear usuario: {e}"

def servicio_consultar_usuarios() -> tuple[list[dict], str]:
    """
    Consulta todos los usuarios de la base de datos.

    Recupera la lista de usuarios y la almacena en el estado. Si hay un error,
    actualiza el mensaje y limpia la lista.
    
    Returns:
        tuple: Una tupla con (lista_usuarios, mensaje)
    """
    usuarios_lista = []
    mensaje_usuario = ""
    try:
        db = SessionLocal()
        usuarios: list[Usuario] = db.query(Usuario).all()
        print(f"[DEBUG] Usuarios consultados: {usuarios}")
        if usuarios:
            usuarios_lista = [
                {"nombre": u.nombre, "email": u.email, "es_admin": u.es_admin}
                for u in usuarios
            ]
            mensaje_usuario = f"{len(usuarios)} usuario(s) encontrados."
        else:
            mensaje_usuario = "No hay usuarios registrados."
    except Exception as e:
        mensaje_usuario = f"Error al consultar usuarios: {e}"
    finally:
        db.close()
    return usuarios_lista, mensaje_usuario


def servicio_filtrar_usuario(nombre: str) -> tuple[list[dict], str]:
    """
    Filtra la lista de usuarios por nombre exacto.

    Busca un usuario por nombre en la base de datos. Si lo encuentra, devuelve ese usuario.
    Si no lo encuentra, devuelve una lista vacía y actualiza el mensaje.

    Args:
        nombre (str): Nombre del usuario a buscar.
        
    Returns:
        tuple: Una tupla con (lista_usuarios_filtrados, mensaje)
    """
    usuarios_lista = []
    mensaje_usuario = ""
    try:
        db = SessionLocal()
        usuario_encontrado: Optional[Usuario] = db.query(Usuario).filter(Usuario.nombre == nombre).first()
        if usuario_encontrado:
            usuarios_lista = [
                {"nombre": usuario_encontrado.nombre,
                    "email": usuario_encontrado.email,
                    "es_admin": usuario_encontrado.es_admin}
            ]
            mensaje_usuario = f"Usuario '{usuario_encontrado.nombre}' encontrado."
        else:
            mensaje_usuario = "No se encontro el usuario."
    except Exception as e:
        mensaje_usuario = f"Error al consultar usuarios: {e}"
    finally:
        db.close()
    return usuarios_lista, mensaje_usuario