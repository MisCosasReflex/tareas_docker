import reflex as rx
from typing import Optional, List
from nueva_app_reflex.db.schemas import UsuarioCreate
from nueva_app_reflex.db.database import SessionLocal
from nueva_app_reflex.db.models import Usuario
from sqlalchemy.exc import IntegrityError
import hashlib
from pydantic import ValidationError


class State(rx.State):
    """
    Estado principal de la aplicación Reflex.
    """
    mensaje_usuario: Optional[str] = None
    usuarios_lista: List[dict] = []

    def registrar_usuario(self, nombre, email, password, es_admin=False) -> None:
        """
        Registra un nuevo usuario en la base de datos.
        """
        try:
            usuario = UsuarioCreate(
                nombre=nombre,
                email=email,
                password=password,
                es_admin=es_admin,
            )
        except ValidationError as e:
            print(f"[DEBUG] Error de validación Pydantic: {e}")
            self.mensaje_usuario = f"Error de validación: {e}"
            return
        
        db = SessionLocal()
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
            print(f"[DEBUG] Usuario guardado: {usuario.nombre}, {usuario.email}, admin={usuario.es_admin}")
            self.mensaje_usuario = f"Usuario '{usuario.nombre}' creado con éxito."
        except IntegrityError:
            db.rollback()
            self.mensaje_usuario = f"El usuario '{usuario.nombre}' o el email '{usuario.email}' ya existen."
        except Exception as e:
            db.rollback()
            self.mensaje_usuario = f"Error al crear usuario: {e}"
        finally:
            db.close()

    def consultar_usuarios(self) -> None:
        """
        Consulta todos los usuarios de la base de datos.
        """
        db = SessionLocal()
        try:
            usuarios = db.query(Usuario).all()
            print(f"[DEBUG] Usuarios consultados: {usuarios}")
            if usuarios:
                self.usuarios_lista = [
                    {"nombre": u.nombre, "email": u.email, "es_admin": u.es_admin}
                    for u in usuarios
                ]
                self.mensaje_usuario = f"{len(usuarios)} usuario(s) encontrados."
            else:
                self.usuarios_lista = []
                self.mensaje_usuario = "No hay usuarios registrados."
        except Exception as e:
            self.usuarios_lista = []
            self.mensaje_usuario = f"Error al consultar usuarios: {e}"
        finally:
            db.close()
