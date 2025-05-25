"""
Página de cambio de contraseña para la aplicación Reflex.

Esta página permite a los usuarios autenticados cambiar su contraseña
de forma segura utilizando el módulo de autenticación.
"""

import reflex as rx
from nueva_app_reflex.state import State
from nueva_app_reflex.components.navbar import navbar
from nueva_app_reflex.auth.adapters.reflex_adapter import require_auth

@require_auth
def change_password() -> rx.Component:
    """
    Renderiza la página de cambio de contraseña.
    
    Esta función está decorada con @require_auth para asegurar
    que solo usuarios autenticados puedan acceder.
    
    Returns:
        rx.Component: Componente Reflex con el formulario de cambio de contraseña.
    """
    return rx.fragment(
        #navbar(),
        rx.vstack(
            rx.heading("Cambiar Contraseña", size="4", mb=6),
            
            # Formulario de cambio de contraseña
            rx.form(
                rx.vstack(
                    rx.form.control(
                        rx.input(
                            type="password",
                            placeholder="Contraseña actual",
                            id="current_password",
                            size="3",
                        ),
                        
                        is_required=True,
                    ),
                    rx.text(
                            "Ingresa tu contraseña actual",
                            font_size="4",
                            color="gray.500",
                            ),
                    rx.form.control(
                        rx.input(
                            type="password",
                            placeholder="Nueva contraseña",
                            id="new_password",
                            size="3",
                        ),

                        is_required=True,
                    ),
                    rx.text(
                            "La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, "
                            "minúsculas, números y caracteres especiales",
                            font_size="4",
                            color="gray.500",
                            ),
                    rx.form.control(
                        rx.input(
                            type="password",
                            placeholder="Confirmar nueva contraseña",
                            id="confirm_password",
                            size="3",
                        ),

                        is_required=True,
                    ),
                    rx.text(
                            "Vuelve a ingresar tu nueva contraseña",
                            font_size="4",
                            color="gray.500",
                            ),
                    rx.button(
                        "Cambiar Contraseña", 
                        type_="submit",
                        size="3",
                        width="100%",
                        color_scheme="blue",
                    ),
                    spacing="4",
                    width="100%",
                    max_width="400px",
                ),
                on_submit=lambda form_data: rx.cond(
                                                form_data.to(dict)["new_password"] == form_data.to(dict)["confirm_password"],
                                                State.change_password(
                                                    form_data.to(dict)["current_password"],
                                                    form_data.to(dict)["new_password"],
                                                ),
                                                State.set_auth_message("Las contraseñas nuevas no coinciden"),
                                            ),
            ),
            
            # Mostrar mensaje de error/éxito
            rx.cond(
                State.auth_message,
                rx.box(
                    rx.text(State.auth_message),
                    
                    rx.cond(
                        (State.auth_message.lower().contains("error") | State.auth_message.lower().contains("incorrecta")),
                        rx.box(
                            rx.text(State.auth_message),
                            padding="3",
                            bg="rgba(255, 200, 200, 0.2)",
                            border_radius="md",
                            width="100%",
                            max_width="400px",
                            text_align="center",
                            margin_top="4",
                        ),
                        rx.box(
                            rx.text(State.auth_message),
                            padding="3",
                            bg="rgba(200, 255, 200, 0.2)",
                            border_radius="md",
                            width="100%",
                            max_width="400px",
                            text_align="center",
                            margin_top="4",
                        ),
                    ),
                    padding="3",
                    border_radius="md",
                    width="100%",
                    max_width="400px",
                    text_align="center",
                    margin_top="4",
                ),
            ),
            
            width="100%",
            height="80vh",
            spacing="6",
            justify="center",
            align="center",
        ),
    )
