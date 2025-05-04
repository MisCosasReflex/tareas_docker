import reflex as rx
from typing import Optional, List
from nueva_app_reflex.db.schemas import UsuarioCreate
from nueva_app_reflex.db.database import SessionLocal
from nueva_app_reflex.db.models import Usuario
from sqlalchemy.exc import IntegrityError
import hashlib
from pydantic import ValidationError
from nueva_app_reflex.users.services import servicio_registrar_usuario, servicio_consultar_usuarios, servicio_filtrar_usuario


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
        self.usuarios_lista, self.mensaje_usuario = servicio_consultar_usuarios()

    def filtrar_usuario(self, nombre: str) -> None:
        """
        Filtra la lista de usuarios por nombre exacto y actualiza el estado.

        Busca un usuario por nombre en la base de datos. Si lo encuentra, actualiza la lista con ese usuario.
        Si no lo encuentra, limpia la lista y actualiza el mensaje.

        Args:
            nombre (str): Nombre del usuario a buscar.
        """
        self.usuarios_lista, self.mensaje_usuario = servicio_filtrar_usuario(nombre)