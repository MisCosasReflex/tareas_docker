"""
Módulo principal de la aplicación Reflex para gestión de tareas.
Define la página principal y configura la aplicación.
"""

import reflex as rx

from rxconfig import config
from nueva_app_reflex.state import State
from nueva_app_reflex.db.schemas import UsuarioCreate


def index() -> rx.Component:
    """
    Página principal de bienvenida de la aplicación Reflex.

    Returns:
        rx.Component: Componente raíz de la página principal.
    """
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            rx.text(
                "Get started by editing ",
                rx.code(f"{config.app_name}/{config.app_name}.py"),
                size="5",
            ),
            rx.link(
                rx.button("Check out our docs!"),
                href="https://reflex.dev/docs/getting-started/introduction/",
                is_external=True,
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )


def registro_usuario() -> rx.Component:
    """
    Página para registrar nuevos usuarios.

    Returns:
        rx.Component: Componente con formulario de registro de usuario.
    """
    def on_submit(fields):
        return State.set_mensaje_usuario("¡Formulario enviado correctamente!")

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
        rx.cond(State.mensaje_usuario, rx.text(State.mensaje_usuario, color="green")),
        margin_top="6",
        max_width="400px",
        align="center",
    )


app = rx.App()
app.add_page(index)
app.add_page(registro_usuario, route="/registro-usuario", title="Registro de Usuario")
