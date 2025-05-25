"""
Script para probar el sistema de logs de la aplicación Reflex.

Este script muestra cómo se registran los mensajes de log en diferentes niveles
y cómo aparecen en los archivos correspondientes.

Uso:
    python tests/test_logs.py
"""

import os
import sys
import time

# Añadir el directorio raíz al path de Python para encontrar el módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nueva_app_reflex.utils.logger import get_logger

def main():
    """Función principal para probar el sistema de logs."""
    # Crear un logger de prueba
    _logger = get_logger("test_logs")
    
    print("=" * 60)
    print("PRUEBA DEL SISTEMA DE LOGS")
    print("=" * 60)
    print(f"Los archivos de log se crearán en: {os.path.abspath('logs/')}")
    print()
    
    # Probar cada nivel de log
    _logger.debug("Este es un mensaje de DEBUG con información técnica detallada")
    _logger.info("Este es un mensaje de INFO para operaciones normales")
    _logger.warning("Este es un mensaje de WARNING sobre una condición inusual")
    _logger.error("Este es un mensaje de ERROR sobre un problema que debe ser atendido")
    _logger.critical("Este es un mensaje CRITICAL sobre un problema grave del sistema")
    
    # Simular un error
    try:
        # Provocar una excepción
        x = 1 / 0
    except Exception as e:
        _logger.exception("Se ha producido un error durante la ejecución")
    
    print("\nMensajes de log generados en todos los niveles.")
    print("Revisa los archivos en el directorio 'logs/' para ver los resultados.")
    print("\nLos archivos generados son:")
    for log_file in os.listdir("logs"):
        file_path = os.path.join("logs", log_file)
        size = os.path.getsize(file_path)
        print(f" - {log_file} ({size} bytes)")
    
    print("\nPrueba completada.")

if __name__ == "__main__":
    main()
