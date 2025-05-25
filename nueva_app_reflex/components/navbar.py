"""
Componente de barra de navegación para la aplicación Reflex.

Este módulo proporciona el componente navbar que muestra los enlaces de navegación
y el estado de autenticación del usuario actual.
"""

import reflex as rx
from nueva_app_reflex.state import State
#from reflex import dropdown_menu

def navbar() -> rx.Component:
    """
    Renderiza la barra de navegación con estado de autenticación.
    
    Returns:
        rx.Component: Componente de barra de navegación.
    """
    return rx.box(
        rx.hstack(
            # Logo / Título
            rx.heading("TaskManager", size="4"),
            
            # Espacio flexible
            rx.spacer(),
            
            # Menú de navegación
            rx.hstack(
                # Mostrar menú completo para usuarios autenticados
                rx.cond(
                    State.is_authenticated,
                    rx.hstack(
                        rx.link("Inicio", href="/", padding="2"),
                        rx.link("Usuarios", href="/consultar_usuarios", padding="2"),
                        rx.link("Registrar Usuario", href="/registro_usuario", padding="2"),
                        rx.spacer(),
                        # Avatar y menú de usuario
                        rx.menu.root(
                            rx.menu.trigger(
                                rx.button(
                                    rx.hstack(
                                        rx.avatar(
                                            name=State.current_user.get("username", ""),
                                            size="2"
                                        ),
                                        rx.text(State.current_user.get("username", "")),
                                        rx.icon("chevron-down")
                                    ),
                                    variant="soft",
                                    size="3"
                                )
                            ),
                            rx.menu.content(
                                rx.menu.item(
                                    rx.link("Perfil", href="/profile", width="100%"),
                                ),
                                rx.menu.item(
                                    rx.link("Cambiar contraseña", href="/change_password", width="100%"),
                                ),
                                rx.menu.separator(),
                                rx.menu.item(
                                    rx.link("Cerrar sesión", href="/logout", width="100%"),
                                ),
                                style={"min-width": "160px"}
                            ),
                        ),
                    ),
                    # Menú reducido para usuarios no autenticados
                    rx.hstack(
                        rx.link("Inicio", href="/", padding="2"),
                        rx.spacer(),
                        rx.button(
                            "Iniciar sesión", 
                            as_child=True,
                            child=rx.link("Iniciar sesión", href="/login"),
                            color_scheme="blue", 
                            variant="outline",
                            size="3",
                            margin_right="2",
                        ),
                        rx.button(
                            "Registrarse", 
                            as_child=True,
                            child=rx.link("Registrarse", href="/register"),
                            color_scheme="blue", 
                            size="3",
                        ),
                    ),
                ),
            ),
            width="100%",
            padding_x="6",
            padding_y="4",
        ),
        width="100%",
        border_bottom="1px solid #eaeaea",
        margin_bottom="6",
    )
