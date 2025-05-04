import reflex as rx
from ..state import State
from ..components.render_lista_usuarios import render_lista_usuarios


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

    # Renderizar la lista de usuarios solo si hay elementos. lista
    lista_component = render_lista_usuarios() 

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