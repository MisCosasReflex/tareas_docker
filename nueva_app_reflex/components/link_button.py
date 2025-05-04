import reflex as rx

def link_button(texto_button:str, url:str) -> rx.Component:
    """Devuelve un enlace con estilo de botón que abre la URL en una nueva pestaña.

    Args:
        texto_button (str): Texto que se mostrará dentro del botón.
        url (str): Dirección web a la que apuntará el enlace.

    Returns:
        rx.Component: Un `rx.link` que envuelve un `rx.button` y, al hacerse clic,
                      abre `url` en una ventana o pestaña nueva.
    
    """
    return rx.link(
        rx.button(texto_button),
        href=url,
        is_external=True,
        )