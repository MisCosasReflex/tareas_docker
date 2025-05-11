import reflex as rx
from nueva_app_reflex.state import State


def page_eliminar_usuario() -> rx.Component:
    """Renderiza la página de eliminación de usuarios.
    
    Returns:
        rx.Component: Componente de página para eliminación de usuarios.
    """
    
    def on_submit(fields: dict) -> None:
        """Maneja el evento de envío del formulario de eliminación de usuario.
        
        Args:
            fields (dict): Diccionario con los datos del formulario.
        """
        if hasattr(fields, "to"):
            fields = fields.to(dict)
        nombre: str = fields.get("nombre", "")
        # Eliminar usuario por nombre
        return State.eliminacion_usuario(nombre)
    
    return rx.container(
        rx.heading("Eliminación de Usuario", size="7"),
        # Mensaje simple sin colores condicionales
        rx.text(
            State.mensaje_usuario,
            font_weight="bold",
            margin_bottom="1em",
        ),
        rx.form(
            rx.vstack(
                rx.input(
                    placeholder="Nombre del usuario a eliminar",
                    id="nombre",
                    required=True,
                ),
                rx.button("Eliminar Usuario", type_="submit"),
                width="100%",
                spacing="4",
                align_items="flex-start",
            ),
            on_submit=on_submit,
        ),
        rx.button(
            "Volver al inicio", 
            on_click=rx.redirect("/"),
            margin_top="1em",
        ),
        padding="2em",
        max_width="800px",
    )