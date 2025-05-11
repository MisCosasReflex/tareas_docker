"""
Ejemplo de uso del sistema de logs en la aplicación Reflex.

Este módulo muestra cómo implementar y utilizar el sistema de logs
en diferentes partes de la aplicación.

Uso:
    Este archivo es solo para referencia y ejemplo, no es necesario
    importarlo o ejecutarlo directamente.
"""

from nueva_app_reflex.utils.logger import get_logger

# Ejemplo de uso básico
def ejemplo_uso_basico():
    # Obtener un logger para este módulo
    _logger = get_logger(__name__)
    
    # Ejemplos de uso en diferentes niveles
    _logger.debug("Este es un mensaje de depuración con detalles técnicos")
    _logger.info("Operación completada correctamente")
    _logger.warning("Se detectó una situación inusual pero no crítica")
    _logger.error("Ha ocurrido un error al procesar la solicitud")
    _logger.critical("Error crítico que impide el funcionamiento normal")

# Ejemplo de uso en servicios
def ejemplo_uso_en_servicios():
    """
    Ejemplo de cómo adaptar los servicios existentes para usar logs.
    
    En lugar de usar print() para depuración, usar _logger.debug()
    """
    _logger = get_logger("nueva_app_reflex.users.services")
    
    # Ejemplo de reemplazo de print con logging
    usuario = {"nombre": "usuario_ejemplo", "email": "ejemplo@mail.com"}
    
    # Antes:
    # print(f"[DEBUG] Usuario guardado: {usuario['nombre']}, {usuario['email']}")
    
    # Después:
    _logger.debug(f"Usuario guardado: {usuario['nombre']}, {usuario['email']}")
    _logger.info(f"Usuario '{usuario['nombre']}' creado con éxito")

# Ejemplo de uso en manejo de excepciones
def ejemplo_manejo_excepciones():
    _logger = get_logger(__name__)
    
    try:
        # Simulación de operación que puede fallar
        resultado = 1 / 0
    except Exception as e:
        # Registrar la excepción con detalles
        _logger.error(f"Error en la operación: {str(e)}", exc_info=True)
        # También es posible usar _logger.exception() que incluye automáticamente 
        # el stack trace:
        _logger.exception("Error en la operación")

# Ejemplo de cómo se integraría en los modelos
def ejemplo_uso_en_modelos():
    _logger = get_logger("nueva_app_reflex.db.models")
    
    # Registro de operaciones en la base de datos
    _logger.debug("Iniciando transacción en la base de datos")
    _logger.info("Nuevo registro creado con ID: 123")
    _logger.warning("Posible consulta ineficiente detectada")

# Ejemplo de uso en el state de Reflex
def ejemplo_uso_en_state():
    _logger = get_logger("nueva_app_reflex.state")
    
    # Registro de cambios de estado
    _logger.debug("Actualizando state.usuarios_lista")
    _logger.info("Estado actualizado después de consultar usuarios")
    _logger.error("Fallo al actualizar el estado")
