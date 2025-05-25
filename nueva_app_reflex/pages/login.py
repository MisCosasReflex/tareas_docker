"""
Página de inicio de sesión para la aplicación Reflex.

Esta página permite a los usuarios autenticarse en el sistema
utilizando el módulo de autenticación implementado.
"""

import reflex as rx
from nueva_app_reflex.state import State
from nueva_app_reflex.components.navbar import navbar


class LoginState(State):
    """Estado específico para la página de login."""
    
    # Variables de estado para el formulario
    username: str = ""
    password: str = ""
    
    def handle_username_change(self, value: str):
        """Actualiza el nombre de usuario."""
        self.username = value
    
    def handle_password_change(self, value: str):
        """Actualiza la contraseña."""
        self.password = value
    
    def handle_login(self):
        """Maneja el inicio de sesión."""
        if self.username and self.password:
            self.login(self.username, self.password)
        else:
            self.set_auth_message("Por favor ingresa usuario y contraseña")


def login() -> rx.Component:
    """
    Renderiza la página de inicio de sesión.
    
    Returns:
        rx.Component: Componente Reflex con el formulario de login.
    """
    return rx.fragment(
        #navbar(),
        rx.vstack(
            rx.heading("Iniciar Sesión", size="4", mb=6),
            
            # Formulario de login
            rx.vstack(
                rx.input(
                    placeholder="Usuario o correo electrónico",
                    value=LoginState.username,
                    on_change=LoginState.handle_username_change,
                    size="3",
                    required=True,
                ),
                rx.input(
                    placeholder="Contraseña",
                    value=LoginState.password,
                    on_change=LoginState.handle_password_change,
                    size="3",
                    type_="password",
                    required=True,
                ),
                rx.button(
                    "Iniciar Sesión", 
                    on_click=LoginState.handle_login,
                    size="3",
                    width="100%",
                    color_scheme="blue",
                ),
                spacing="4",
                width="100%",
                max_width="400px",
            ),
            
            # Mostrar mensaje de error/éxito
            rx.cond(
                State.auth_message,
                rx.box(
                    rx.text(State.auth_message),
                    padding="3",
                    bg=rx.cond(
                        ~State.is_authenticated,
                        "rgba(255, 200, 200, 0.2)",
                        "rgba(200, 255, 200, 0.2)"
                    ),
                    border_radius="md",
                    width="100%",
                    max_width="400px",
                    text_align="center",
                    margin_top="4",
                ),
            ),
            
            # Enlace a registro
            rx.hstack(
                rx.text("¿No tienes una cuenta?"),
                rx.link(
                    "Regístrate", 
                    href="/register", 
                    color="blue.500", 
                    text_decoration="underline"
                ),
                margin_top="5",
            ),
            
            # Redirigir si está autenticado
            rx.cond(
                State.is_authenticated,
                rx.script("window.location.href = '/'")
            ),
            
            width="100%",
            height="80vh",
            spacing="6",
            justify="center",
            align="center",
        ),
    )
