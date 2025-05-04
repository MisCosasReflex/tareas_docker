import reflex as rx
from ..state import State

def render_lista_usuarios() -> rx.Component:
    """Renderiza un listado de usuarios desde el estado global de la aplicación.

    Esta función comprueba si `State.usuarios_lista` contiene elementos y, en caso afirmativo,
    construye un componente de tipo `rx.vstack` que agrupa un `rx.box` por cada usuario. Cada caja
    muestra el nombre, el correo y el rol (“Admin” o “Usuario”) del usuario, con un estilo de
    separación horizontal y un borde inferior ligero. Si no hay elementos en la lista, devuelve `None`.

    Args:
        (ninguno): esta función no recibe parámetros; funciona siempre sobre
        `State.usuarios_lista`, que debe ser una lista de diccionarios con las claves:
          - `"nombre"` (str): nombre completo del usuario.
          - `"email"` (str): dirección de correo.
          - `"es_admin"` (bool): indica si el usuario tiene rol de administrador.

    Returns:
        rx.Component | None:
            - Si `State.usuarios_lista` está vacío o es falsy, retorna `None`.
            - En caso contrario, retorna un `rx.vstack` con:
                * Un `rx.foreach` que itera sobre la lista.
                * Para cada usuario `u`, un `rx.box` con:
                    - `rx.text(f"👤 {u['nombre']} | {u['email']} | " + rx.cond(u['es_admin'], "Admin", "Usuario"))`
                    - `padding_y="1"` para espacio vertical.
                    - `border_bottom="1px solid #eee"` para delimitar cada elemento.

    Detalles de implementación:
        1. `rx.cond(State.usuarios_lista, ... , None)`:  
           - Evalúa la lista como condición booleana; si está vacía, salta la renderización.
        2. `rx.vstack(...)`:  
           - Organiza los elementos en columna, con `spacing="2"`, `align="start"` y `width="100%"`.
        3. `rx.foreach(State.usuarios_lista, lambda u: ...)`:  
           - Genera dinámicamente un componente por cada entrada de la lista.
        4. Uso de emoticono “👤” y `rx.cond(u['es_admin'], "Admin", "Usuario")` para mejorar la lectura.

    Ejemplo de uso:
        ```python
        import reflex as rx
        from components.lista_usuarios import render_lista_usuarios

        @rx.page(route="/usuarios", title="Gestión de Usuarios")
        def usuarios_page() -> rx.Component:
            return rx.container(
                rx.heading("Usuarios registrados", size="xl"),
                render_lista_usuarios(),
            )
        ```    
    """
    lista_component = rx.cond(
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
    return lista_component