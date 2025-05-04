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
from nueva_app_reflex.pages.registro_usuario import registro_usuario
from nueva_app_reflex.pages.consultar_usuarios import consultar_usuarios
from nueva_app_reflex.components.link_button import link_button

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
            link_button("Agrega un usuario nuevo", "http://localhost:3000/registro-usuario/"),
            link_button("Consulta los usuarios agregados", "http://localhost:3000/consultar-usuarios/"),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )



app: rx.App = rx.App()
# Registrar las páginas principales de la aplicación
app.add_page(index)
app.add_page(registro_usuario, route="/registro-usuario", title="Registro de Usuario")
app.add_page(consultar_usuarios, route="/consultar-usuarios", title="Consulta de Usuarios")