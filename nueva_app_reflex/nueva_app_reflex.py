"""
Módulo principal de la aplicación Reflex para gestión de tareas.

Este módulo define la estructura principal de la aplicación web, incluyendo:
- La página de bienvenida (index)
- Sistema de autenticación de usuarios
- Gestión de perfil y contraseñas
- Registro y consulta de usuarios
- La configuración de rutas y páginas en la aplicación Reflex

Uso:
    Ejecutar la aplicación con Reflex y acceder a las rutas definidas.
"""

import reflex as rx

from rxconfig import config
from reflex.vars import Var
from nueva_app_reflex.state import State, auth_manager
from nueva_app_reflex.db.schemas import UsuarioCreate
from typing import Dict, List

# Importar páginas de la aplicación
from nueva_app_reflex.pages.registro_usuario import registro_usuario
from nueva_app_reflex.pages.consultar_usuarios import consultar_usuarios
from nueva_app_reflex.pages.eliminar_usuario import page_eliminar_usuario
from nueva_app_reflex.components.link_button import link_button

# Importar páginas de autenticación
from nueva_app_reflex.pages.login import login
from nueva_app_reflex.pages.register import register
from nueva_app_reflex.pages.profile import profile
from nueva_app_reflex.pages.change_password import change_password

# Importar componentes
from nueva_app_reflex.components.navbar import navbar

def index() -> rx.Component:
    """
    Renderiza la página principal de bienvenida de la aplicación Reflex.

    Esta página muestra enlaces para navegar hacia los diferentes módulos de la aplicación
    y está adaptada para mostrar diferentes opciones según el estado de autenticación.

    Returns:
        rx.Component: Componente raíz de la página principal.
    """
    return rx.fragment(
        #navbar(),
        rx.text("Hola"),
        rx.container(
            rx.vstack(
                rx.heading("Sistema de Gestión de Tareas", size="8", color="blue.500"),
                rx.text(
                    "Una aplicación con autenticación segura para gestionar tareas y usuarios",
                    font_size="5",
                    color="gray.600",
                    mb=6,
                ),
                
                # Mostrar diferentes opciones según estado de autenticación
                rx.cond(
                    State.is_authenticated,
                    # Opciones para usuarios autenticados
                    rx.vstack(
                        rx.heading(f"Bienvenido, {State.current_user.get('username', '')}", size="4", mb=4),
                        rx.hstack(
                            rx.card(
                                rx.vstack(
                                    rx.icon("user", font_size="2xl", color="blue.500", mb=2),
                                    rx.heading("Gestión de Usuarios", size="3"),
                                    rx.text("Administra los usuarios del sistema", color="gray.600", font_size="sm"),
                                    rx.button("Ir", on_click=rx.redirect("/consultar-usuarios"), size="3"),
                                    spacing="2",
                                    align_items="center",
                                ),
                                height="200px",
                                width="200px",
                            ),
                            rx.card(
                                rx.vstack(
                                    rx.icon("plus", font_size="2xl", color="green.500", mb=2),
                                    rx.heading("Registrar Usuario", size="3"),
                                    rx.text("Añade nuevos usuarios al sistema", color="gray.600", font_size="3"),
                                    rx.button("Ir", on_click=rx.redirect("/registro-usuario"), size="3", color_scheme="green"),
                                    spacing="2",
                                    align_items="center",
                                ),
                                height="200px",
                                width="200px",
                            ),
                            rx.card(
                                rx.vstack(
                                    rx.icon("trash", font_size="2xl", color="red.500", mb=2),
                                    rx.heading("Eliminar Usuario", size="3"),
                                    rx.text("Elimina usuarios del sistema", color="gray.600", font_size="3"),
                                    rx.button("Ir", on_click=rx.redirect("/eliminar-usuario"), size="3", color_scheme="red"),
                                    spacing="2",
                                    align_items="center",
                                ),
                                height="200px",
                                width="200px",
                            ),
                            spacing="6",
                            justify="center",
                            width="100%",
                        ),
                    ),
                    # Opciones para usuarios no autenticados
                    rx.vstack(
                        rx.heading("¡Bienvenido a TaskManager!", size="5", mb=4),
                        rx.text("Por favor, inicia sesión o regístrate para acceder a todas las funcionalidades", mb=6),
                        rx.hstack(
                            rx.button(
                                "Iniciar Sesión", 
                                on_click=rx.redirect("/login"), 
                                size="3", 
                                color_scheme="blue",
                            ),
                            rx.button(
                                "Registrarse", 
                                on_click=rx.redirect("/register"), 
                                size="3", 
                                variant="outline",
                                color_scheme="blue",
                            ),
                            spacing="4",
                        ),
                    ),
                ),
                spacing="6",
                justify="center",
                align_items="center",
                min_height="80vh",
                padding_bottom="8",
            ),
            rx.color_mode.button(position="fixed-corner"),
        ),
    )



# Inicializar estado

    
# Crear la aplicación Reflex
app = rx.App()

# Registrar las páginas principales de la aplicación
app.add_page(index, title="TaskManager - Gestión de Tareas", on_load=State.on_app_load)

# Páginas de gestión de usuarios (protegidas)
app.add_page(registro_usuario, route="/registro-usuario", title="Registro de Usuario")
app.add_page(consultar_usuarios, route="/consultar-usuarios", title="Consulta de Usuarios")
app.add_page(page_eliminar_usuario, route="/eliminar-usuario", title="Eliminación de Usuario")

# Páginas de autenticación
app.add_page(login, route="/login", title="Iniciar Sesión")
app.add_page(register, route="/register", title="Registro de Usuario")
app.add_page(profile, route="/profile", title="Perfil de Usuario")
app.add_page(change_password, route="/change_password", title="Cambiar Contraseña")