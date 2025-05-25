"""
Página de perfil de usuario para la aplicación Reflex.

Esta página muestra la información del usuario autenticado
y permite acceder a funcionalidades relacionadas con la cuenta.
"""

import reflex as rx
from nueva_app_reflex.state import State
from nueva_app_reflex.components.navbar import navbar
from nueva_app_reflex.components.link_button import link_button
from nueva_app_reflex.auth.adapters.reflex_adapter import require_auth

@require_auth
def profile() -> rx.Component:
    """
    Renderiza la página de perfil del usuario.
    
    Esta función está decorada con @require_auth para asegurar
    que solo usuarios autenticados puedan acceder.
    
    Returns:
        rx.Component: Componente Reflex con la información del perfil.
    """
    return rx.fragment(
        #navbar(),
        rx.vstack(
            rx.heading("Perfil de Usuario", size="4", mb=6),
            
            # Tarjeta de perfil
            rx.card(
                rx.vstack(
                    # Avatar grande y nombre de usuario
                    rx.center(
                        rx.avatar(
                            name=State.current_user.get("username", ""),
                            size="4",
                            mb=4,
                        ),
                    ),
                    rx.heading(
                        State.current_user.get("username", ""),
                        size="3",
                        color="blue.500",
                        text_align="center",
                    ),
                    rx.divider(my=4),
                    
                    # Información del usuario
                    rx.hstack(
                        rx.text("Correo electrónico:", font_weight="bold"),
                        rx.text(State.current_user.get("email", "")),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Rol:", font_weight="bold"),
                        rx.text(
                            rx.cond(
                             State.current_user.get("es_admin", False),
                             "Administrador",
                             "Usuario"
                          )

                        ),
                        width="100%",
                    ),
                    rx.cond(
                        State.current_user.get("is_verified", False),
                        rx.badge("Email verificado", color_scheme="green"),
                        rx.badge("Email no verificado", color_scheme="yellow"),
                    ),
                    
                    # Acciones de usuario
                    rx.divider(my=4),
                    rx.heading("Acciones", size="2", mb=2),
                    rx.hstack(
                        link_button("Cambiar contraseña", "/change_password"),
                        rx.button(
                            "Cerrar sesión",
                            on_click=State.logout,
                            color_scheme="red",
                            size="2",
                            margin="1",
                        ),
                        justify="center",
                        spacing="3",
                    ),
                    
                    spacing="3",
                    width="100%",
                    align_items="flex-start",
                ),
                width="100%",
                max_width="500px",
                flex_wrap="wrap",
            ),
            
            width="100%",
            height="80vh",
            spacing="6",
            justify="center",
            align="center",
        ),
    )
