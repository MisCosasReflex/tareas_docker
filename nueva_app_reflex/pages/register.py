"""
Página de registro de usuarios para la aplicación Reflex.

Esta página permite a los nuevos usuarios registrarse en el sistema
utilizando el módulo de autenticación implementado.
"""

import reflex as rx
from nueva_app_reflex.state import State
from nueva_app_reflex.components.navbar import navbar

class RegisterState(State):
    """Estado específico para la página de registro."""
    
    # Variables de estado para el formulario
    username: str = ""
    email: str = ""
    password: str = ""
    is_admin: bool = False
    
    def handle_username_change(self, value: str):
        """Actualiza el nombre de usuario."""
        self.username = value
    
    def handle_email_change(self, value: str):
        """Actualiza el correo electrónico."""
        self.email = value
    
    def handle_password_change(self, value: str):
        """Actualiza la contraseña."""
        self.password = value
    
    def handle_is_admin_change(self, value: bool):
        """Actualiza el estado de administrador."""
        self.is_admin = value
    
    def handle_register(self):
        """Maneja el registro de usuario."""
        if self.username and self.email and self.password:
            self.register(self.username, self.email, self.password, self.is_admin)
        else:
            self.set_auth_message("Por favor completa todos los campos requeridos")


def register() -> rx.Component:
    """
    Renderiza la página de registro de usuarios.
    
    Returns:
        rx.Component: Componente Reflex con el formulario de registro.
    """
    return rx.fragment(
        #navbar(),
        rx.vstack(
            rx.heading("Registro de Usuario", size="4", mb=6),
            
            # Formulario de registro
            rx.vstack(
                rx.vstack(
                    rx.input(
                        placeholder="Nombre de usuario",
                        value=RegisterState.username,
                        on_change=RegisterState.handle_username_change,
                        size="3",
                    ),
                    rx.text("Elige un nombre de usuario único", 
                           font_size="sm", 
                           color="gray.500",
                           mb=2),
                    align_items="start",
                    width="100%",
                ),
                rx.vstack(
                    rx.input(
                        placeholder="Correo electrónico",
                        value=RegisterState.email,
                        on_change=RegisterState.handle_email_change,
                        type_="email",
                        size="3",
                    ),
                    rx.text("Ingresa un correo electrónico válido",
                           font_size="sm", 
                           color="gray.500",
                           mb=2),
                    align_items="start",
                    width="100%",
                ),
                rx.vstack(
                    rx.input(
                        placeholder="Contraseña",
                        value=RegisterState.password,
                        on_change=RegisterState.handle_password_change,
                        type_="password",
                        size="3",
                    ),
                    rx.text(
                        "La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, "
                        "minúsculas, números y caracteres especiales",
                        font_size="sm", 
                        color="gray.500",
                        mb=2
                    ),
                    align_items="start",
                    width="100%",
                ),
                rx.checkbox(
                    "Registrar como administrador", 
                    checked=RegisterState.is_admin,
                    on_change=RegisterState.handle_is_admin_change,
                    color_scheme="blue",
                    mb=4,
                ),
                rx.button(
                    "Registrar", 
                    on_click=RegisterState.handle_register,
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
                        (State.auth_message.lower().contains("error")) | (State.auth_message.lower().contains("ya existe")),
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
            
            # Enlace a inicio de sesión
            rx.hstack(
                rx.text("¿Ya tienes una cuenta?"),
                rx.link(
                    "Inicia sesión", 
                    href="/login", 
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
            height="90vh",
            spacing="6",
            justify="center",
            align="center",
        ),
    )
