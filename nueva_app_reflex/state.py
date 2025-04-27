import reflex as rx
from typing import Optional
from nueva_app_reflex.db.schemas import UsuarioCreate
from nueva_app_reflex.db.database import SessionLocal
from nueva_app_reflex.db.models import Usuario
from sqlalchemy.exc import IntegrityError
import hashlib

class State(rx.State):
    """
    Estado principal de la aplicación Reflex.

    Puedes agregar aquí variables y métodos que gestionen el estado global de la app.
    """
    mensaje_usuario: Optional[str] = None

    def registrar_usuario(self, usuario: UsuarioCreate) -> None:
        """
        Registra un nuevo usuario en la base de datos.

        Args:
            usuario (UsuarioCreate): Datos validados del usuario.
                - nombre: nombre de usuario único
                - email: dirección de correo electrónico única
                - password: contraseña en texto plano (será hasheada)
                - es_admin: si el usuario es administrador o no
        """
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
            self.mensaje_usuario = f"Usuario '{usuario.nombre}' creado con éxito."
        except IntegrityError:
            db.rollback()
            self.mensaje_usuario = f"El usuario '{usuario.nombre}' o el email '{usuario.email}' ya existen."
        except Exception as e:
            db.rollback()
            self.mensaje_usuario = f"Error al crear usuario: {e}"
        finally:
            db.close()
