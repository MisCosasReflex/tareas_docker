"""
Módulo principal de la aplicación Reflex para gestión de tareas.

Este módulo define la estructura principal de la aplicación web, incluyendo:
- La página de bienvenida (index)
- El formulario de registro de usuarios
- La consulta de usuarios registrados
- La configuración de rutas y páginas en la aplicación Reflex

Uso:
    Ejecutar la aplicación con Reflex y acceder a las rutas definidas.
"""

import reflex as rx

from rxconfig import config
from reflex.vars import Var
from nueva_app_reflex.state import State
from nueva_app_reflex.db.schemas import UsuarioCreate
from typing import Dict, List


def index() -> rx.Component:
    """
    Renderiza la página principal de bienvenida de la aplicación Reflex.

    Esta página muestra enlaces para navegar hacia el registro de usuarios y la consulta de usuarios registrados.
    Incluye el logo de la aplicación y un botón para cambiar el modo de color.

    Returns:
        rx.Component: Componente raíz de la página principal.
    """
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Aplicacion de tareas por hacer", size="9"),
            rx.link(
                rx.button("Agrega un usuario nuevo"),
                href="http://localhost:3000/registro-usuario/",
                is_external=True,
            ),
            rx.link(
                rx.button("Consulta los usuarios agregados"),
                href="http://localhost:3000/consultar-usuarios/",
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


def consultar_usuarios() -> rx.Component:
    """
    Renderiza la página de consulta y búsqueda de usuarios registrados.

    Permite consultar la lista completa de usuarios o filtrar por nombre mediante un formulario de búsqueda.
    Muestra mensajes de éxito o error según el resultado de la consulta.

    Returns:
        rx.Component: Componente con la lista de usuarios y el formulario de búsqueda.
    """
    # Obtener el mensaje actual del estado, o cadena vacía si no hay mensaje
    mensaje: Var[str] = rx.cond(
        State.mensaje_usuario,
        State.mensaje_usuario,
        ""
    )

    # Determinar el color del mensaje según si es error o éxito
    color_mensaje: Var[str] = rx.cond(
        mensaje.startswith("Error"),
        "red",
        "green",
    )

    # Renderizar la lista de usuarios solo si hay elementos
    lista_component: rx.Component = rx.cond(
        State.usuarios_lista,
        rx.vstack(
            rx.foreach(
                State.usuarios_lista,
                lambda u: rx.box(
                    rx.text(
                        f"👤 {u['nombre']} | {u['email']} | "
                        + rx.cond(u['es_admin'], "Admin", "Usuario")
                    ),
                    padding_y="1",
                    border_bottom="1px solid #eee",
                ),
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        None
    )

    def on_submit(fields: dict) -> None:
        """
        Maneja el evento de envío del formulario de búsqueda de usuario por nombre.

        Extrae el nombre del formulario y llama a la función de filtrado en el estado global.

        Args:
            fields (dict): Diccionario con los datos del formulario.
        """
        if hasattr(fields, "to"):
            fields = fields.to(dict)
        nombre: str = fields.get("nombre", "")
        # Filtrar usuario por nombre
        return State.filtrar_usuario(nombre)

    return rx.container(
        rx.heading("Consulta de Usuarios", size="7"),
        rx.button("Consultar Usuarios", on_click=State.consultar_usuarios),
        rx.heading("Busqueda de usuario", size="7"),
        rx.form(
            rx.vstack(
                rx.input(
                    name="nombre",
                    placeholder="Nombre de usuario",
                    required=True,
                ),
                rx.button("Buscar", type_="submit"),
            ),
            on_submit=on_submit,
            reset_on_submit=True,
        ),
        rx.text(mensaje, color=color_mensaje),
        lista_component,
        margin_top="6",
        max_width="400px",
        align="center",
    )


def filtrar_usuario() -> None:
    """
    Esta función es un placeholder y no se utiliza en la aplicación.
    """
    pass


app: rx.App = rx.App()
# Registrar las páginas principales de la aplicación
app.add_page(index)
app.add_page(registro_usuario, route="/registro-usuario", title="Registro de Usuario")
app.add_page(consultar_usuarios, route="/consultar-usuarios", title="Consulta de Usuarios")