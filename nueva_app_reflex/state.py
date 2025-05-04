import reflex as rx
from typing import Optional, List
from nueva_app_reflex.db.schemas import UsuarioCreate
from nueva_app_reflex.db.database import SessionLocal
from nueva_app_reflex.db.models import Usuario
from sqlalchemy.exc import IntegrityError
import hashlib
from pydantic import ValidationError
from nueva_app_reflex.users.services import servicio_registrar_usuario


class State(rx.State):
    """
    Estado principal de la aplicación Reflex.

    Esta clase gestiona el estado global de la aplicación, incluyendo:
    - Mensajes para el usuario sobre operaciones realizadas.
    - Lista de usuarios consultados.

    Métodos principales:
        - registrar_usuario: Registra un nuevo usuario en la base de datos.
        - consultar_usuarios: Consulta todos los usuarios registrados.
        - filtrar_usuario: Filtra un usuario por nombre.
    """
    mensaje_usuario: Optional[str] = None  # Mensaje de éxito o error para mostrar en la UI
    usuarios_lista: List[dict] = []        # Lista de usuarios mostrados en la UI

    def registrar_usuario(self, nombre: str, email: str, password: str, es_admin: bool = False) -> None:
        """
        Registra un nuevo usuario en la base de datos.

        Valida los datos usando Pydantic, genera el hash de la contraseña y guarda el usuario en la base de datos.
        Maneja errores de validación y de integridad (usuarios duplicados).

        Args:
            nombre (str): Nombre de usuario.
            email (str): Correo electrónico del usuario.
            password (str): Contraseña en texto plano.
            es_admin (bool, opcional): Indica si el usuario es administrador. Por defecto False.
        """
        self.mensaje_usuario = servicio_registrar_usuario(nombre, email, password, es_admin)

    def consultar_usuarios(self) -> None:
        """
        Consulta todos los usuarios de la base de datos y actualiza la lista y el mensaje de estado.

        Recupera la lista de usuarios y la almacena en el estado. Si hay un error,
        actualiza el mensaje y limpia la lista.
        """
        db = SessionLocal()
        try:
            usuarios: list[Usuario] = db.query(Usuario).all()
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

    def filtrar_usuario(self, nombre: str) -> None:
        """
        Filtra la lista de usuarios por nombre exacto y actualiza el estado.

        Busca un usuario por nombre en la base de datos. Si lo encuentra, actualiza la lista con ese usuario.
        Si no lo encuentra, limpia la lista y actualiza el mensaje.

        Args:
            nombre (str): Nombre del usuario a buscar.
        """
        db = SessionLocal()
        try:
            usuario_encontrado: Optional[Usuario] = db.query(Usuario).filter(Usuario.nombre == nombre).first()
            if usuario_encontrado:
                self.usuarios_lista = [
                    {"nombre": usuario_encontrado.nombre,
                     "email": usuario_encontrado.email,
                     "es_admin": usuario_encontrado.es_admin}
                ]
                self.mensaje_usuario = f"Usuario '{usuario_encontrado.nombre}' encontrado."
            else:
                self.usuarios_lista = []
                self.mensaje_usuario = "No se encontro el usuario."
        except Exception as e:
            self.mensaje_usuario = f"Error al consultar usuarios: {e}"
        finally:
            db.close()