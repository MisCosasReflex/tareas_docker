import reflex as rx
from typing import Optional, List, Dict, Any, Type
from nueva_app_reflex.db.schemas import UsuarioCreate
from nueva_app_reflex.db.database import SessionLocal
from nueva_app_reflex.db.models import Usuario
from sqlalchemy.exc import IntegrityError
import hashlib
from pydantic import ValidationError
from nueva_app_reflex.users.services import servicio_registrar_usuario, servicio_consultar_usuarios, servicio_filtrar_usuario, servicio_eliminar_usuario

# Importar sistema de autenticación
from nueva_app_reflex.auth.adapters.reflex_adapter import AuthState
from nueva_app_reflex.auth.core.auth import AuthManager
from nueva_app_reflex.auth.utils.model_adapter import adapt_usuario_model


# Configurar AuthManager para la aplicación
def get_user_by_username(username: str) -> Optional[Any]:
    """Obtiene un usuario por su nombre de usuario."""
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.nombre == username).first()
        if usuario:
            return adapt_usuario_model(usuario)
        return None
    finally:
        db.close()

def get_user_by_email(email: str) -> Optional[Any]:
    """Obtiene un usuario por su email."""
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if usuario:
            return adapt_usuario_model(usuario)
        return None
    finally:
        db.close()

def save_user(user_data: Dict[str, Any]) -> None:
    """Guarda un nuevo usuario en la base de datos."""
    # Utilizamos el servicio existente de registro
    servicio_registrar_usuario(
        nombre=user_data["username"],
        email=user_data["email"],
        password=user_data["password_hash"],  # Ya viene hasheado
        es_admin=user_data.get("es_admin", False)
    )

def update_user(user) -> None:
    """Actualiza un usuario existente."""
    db = SessionLocal()
    try:
        original_user = user.user  # Obtener el usuario original del adaptador
        db.merge(original_user)
        db.commit()
    finally:
        db.close()

# Crear instancia global del AuthManager
auth_manager = AuthManager(
    user_model=adapt_usuario_model,
    get_user_by_username=get_user_by_username,
    get_user_by_email=get_user_by_email,
    save_user=save_user,
    update_user=update_user
)


class State(AuthState):
    """
    Estado principal de la aplicación Reflex.

    Esta clase gestiona el estado global de la aplicación, incluyendo:
    - Mensajes para el usuario sobre operaciones realizadas.
    - Lista de usuarios consultados.
    - Estado del menú de navegación.

    Atributos:
        mensaje_usuario (str): Mensaje de éxito o error para mostrar en la UI
        usuarios_lista (list[dict]): Lista de usuarios mostrados en la UI
        is_menu_open (bool): Estado del menú de navegación

    Métodos principales:
        - registrar_usuario: Registra un nuevo usuario en la base de datos.
        - consultar_usuarios: Consulta todos los usuarios registrados.
        - filtrar_usuario: Busca un usuario por nombre exacto.
        - toggle_menu: Alterna el estado del menú de navegación.
    """
    mensaje_usuario: Optional[str] = None  # Mensaje de éxito o error para mostrar en la UI
    usuarios_lista: List[dict] = []        # Lista de usuarios mostrados en la UI
    is_menu_open: bool = False



    @rx.event(background=True)
    async def on_app_load(self):
        """Función que se ejecuta al cargar la aplicación."""
        # Configurar el sistema de autenticación
        self.set_auth_manager(auth_manager)



    def registrar_usuario(self, nombre: str, email: str, password: str, es_admin: bool = False) -> None:
        """
        Registra un nuevo usuario en la base de datos.

        Llama al servicio de registro de usuarios con los datos proporcionados y actualiza
        el mensaje de estado con el resultado de la operación.

        Args:
            nombre (str): Nombre de usuario.
            email (str): Correo electrónico del usuario.
            password (str): Contraseña en texto plano.
            es_admin (bool, opcional): Indica si el usuario es administrador. Por defecto False.

        Returns:
            None: El método actualiza el estado interno de la aplicación.
        """
        self.mensaje_usuario = servicio_registrar_usuario(nombre, email, password, es_admin)

    def consultar_usuarios(self) -> None:
        """
        Consulta todos los usuarios registrados en la base de datos.

        Llama al servicio de consulta de usuarios y actualiza el estado con los resultados.

        Returns:
            None: El método actualiza el estado interno de la aplicación.
        """
        self.usuarios_lista, self.mensaje_usuario = servicio_consultar_usuarios()

    def filtrar_usuario(self, nombre: str) -> None:
        """
        Busca un usuario por nombre exacto en la base de datos.

        Llama al servicio de filtrado de usuarios con el nombre proporcionado y actualiza
        el estado con los resultados.

        Args:
            nombre (str): Nombre exacto del usuario a buscar.

        Returns:
            None: El método actualiza el estado interno de la aplicación.
        """
        self.usuarios_lista, self.mensaje_usuario = servicio_filtrar_usuario(nombre)

    def eliminacion_usuario(self, nombre:str) -> None:
        """Elimina un usuario por su nombre.
        
        Args:
            nombre (str): Nombre del usuario a eliminar.
        """
        servicio_eliminar_usuario(nombre)
        self.mensaje_usuario = f"Usuario {nombre} eliminado con éxito"
        # Actualizamos la lista de usuarios sin sobrescribir el mensaje
        usuarios, _ = servicio_consultar_usuarios()
        self.usuarios_lista = usuarios