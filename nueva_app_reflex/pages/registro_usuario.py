import reflex as rx
from ..state import State

def registro_usuario() -> rx.Component:
    """
    Renderiza la página de registro de nuevos usuarios.

    Esta página incluye un formulario para ingresar el nombre, correo electrónico, contraseña y si el usuario es administrador.
    Al enviar el formulario, se llama a la función de registro en el estado global.

    Returns:
        rx.Component: Componente con el formulario de registro de usuario.
    """
    def on_submit(fields: dict) -> None:
        """
        Maneja el evento de envío del formulario de registro de usuario.

        Extrae los campos del formulario y llama a la función de registro de usuario en el estado global.

        Args:
            fields (dict): Diccionario con los datos del formulario.
        """
        # Convertir a dict si es necesario
        if hasattr(fields, "to"):
            fields = fields.to(dict)
        nombre: str = fields.get("nombre", "")
        email: str = fields.get("email", "")
        password: str = fields.get("password", "")
        es_admin: bool = fields.get("es_admin", False)
        # Registrar usuario en el estado global
        return State.registrar_usuario(nombre, email, password, es_admin)

    return rx.container(
        rx.heading("Registro de Usuario", size="7"),
        rx.form(
            rx.vstack(
                rx.input(
                    name="nombre",
                    placeholder="Nombre de usuario",
                    required=True,
                ),
                rx.input(
                    name="email",
                    placeholder="Correo electrónico",
                    required=True,
                ),
                rx.input(
                    name="password",
                    placeholder="Contraseña",
                    type="password",
                    required=True,
                ),
                rx.checkbox(
                    name="es_admin",
                    label="¿Es administrador?",
                    default_checked=False,
                ),
                rx.button("Registrar", type_="submit"),
            ),
            on_submit=on_submit,
            reset_on_submit=True,
        ),
        # Mostrar mensaje de éxito o error si existe
        rx.cond(State.mensaje_usuario, rx.text(State.mensaje_usuario, color="green")),
        margin_top="6",
        max_width="400px",
        align="center",
    )