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
    Página principal de bienvenida de la aplicación Reflex.

    Muestra enlaces a las páginas de registro y consulta de usuarios.

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
    Página para registrar nuevos usuarios.

    Muestra un formulario para registrar un nuevo usuario, incluyendo nombre,
    correo electrónico, contraseña y si es administrador.

    Returns:
        rx.Component: Componente con formulario de registro de usuario.
    """
    def on_submit(fields):
        """
        Maneja el evento de envío del formulario de registro.

        Extrae los campos del formulario y llama a la función de registro de usuario
        en el estado global.

        Args:
            fields (dict): Diccionario con los datos del formulario.

        Returns:
            None
        """
        # Extraer los campos individuales y pasarlos como argumentos al método del State
        if hasattr(fields, "to"):
            fields = fields.to(dict)
        nombre = fields.get("nombre")
        email = fields.get("email")
        password = fields.get("password")
        es_admin = fields.get("es_admin", False)
        
        # Llamada a la función para registrar el usuario
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
        rx.cond(State.mensaje_usuario, rx.text(State.mensaje_usuario, color="green")),
        margin_top="6",
        max_width="400px",
        align="center",
    )


def consultar_usuarios() -> rx.Component:
    """
    Página para consultar los usuarios registrados en la aplicación.

    Permite consultar y mostrar la lista de usuarios registrados, mostrando
    nombre, email y rol (admin o usuario). También muestra mensajes de éxito o error.

    Returns:
        rx.Component: Componente con lista de usuarios.
    """
    # 1. Mensaje de usuario: si existe, mostrarlo; si no, cadena vacía.
    mensaje: Var[str] = rx.cond(
        State.mensaje_usuario,  # si es truthy (no None ni empty)
        State.mensaje_usuario,  # se muestra ese texto
        ""                      # si no, cadena vacía
    )

    # 2. Color del mensaje: rojo si empieza con "Error", verde en otro caso.
    color_mensaje: Var[str] = rx.cond(
        mensaje.startswith("Error"),  # usamos 'mensaje', nunca null
        "red",
        "green",
    )

    # 3. Componente de la lista: sólo renderizar si la lista de usuarios no está vacía.
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

    # 4. Componente de la lista: sólo renderizar si la lista de usuarios no está vacía.
    lista_component_filtrada: rx.Component = rx.cond(
        State.usuarios_filtrados,
        rx.vstack(
            rx.foreach(
                State.usuarios_filtrados,
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


    def on_submit(fields):
        """

        """
        # Extraer los campos individuales y pasarlos como argumentos al método del State
        if hasattr(fields, "to"):
            fields = fields.to(dict)
        nombre = fields.get("nombre","")       
        # Llamada a la función para registrar el usuario
        return State.filtrar_usuario(nombre)
        

    # 4. Montaje final del contenedor
    return rx.container(
        rx.heading("Consulta de Usuarios", size="7"),
        rx.button("Consultar Usuarios", on_click=State.consultar_usuarios),
        rx.text(mensaje, color=color_mensaje),
        lista_component,
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
        lista_component_filtrada,

        margin_top="6",
        max_width="400px",
        align="center",
        
    )





def filtrar_usuario() -> rx.Component:
    pass


app = rx.App()
app.add_page(index)
app.add_page(registro_usuario, route="/registro-usuario", title="Registro de Usuario")
app.add_page(consultar_usuarios, route="/consultar-usuarios", title="Consulta de Usuarios")