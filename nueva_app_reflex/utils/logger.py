"""
Módulo de configuración de logging para la aplicación Reflex.

Este módulo proporciona un sistema de logs centralizado siguiendo buenas prácticas.
Permite registrar mensajes en archivos de log con diferentes niveles de severidad
y formatos consistentes.

Uso:
    from nueva_app_reflex.utils.logger import get_logger
    
    # Obtener logger para un módulo específico
    logger = get_logger(__name__)
    
    # Usar el logger en diferentes niveles
    logger.debug("Mensaje de depuración detallado")
    logger.info("Información general del proceso")
    logger.warning("Advertencia que no interrumpe la ejecución")
    logger.error("Error que permite continuar la ejecución")
    logger.critical("Error grave que podría detener la aplicación")
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
import datetime

# Configuración de directorio para logs
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Nombre base para los archivos de log
BASE_LOG_FILENAME = os.path.join(LOG_DIR, "nueva_app_reflex.log")

# Configuración de formato para logs
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Tamaño máximo para rotación de logs (10MB)
MAX_LOG_SIZE_BYTES = 10 * 1024 * 1024
# Número de archivos de backup a mantener
BACKUP_COUNT = 5

# Niveles de log disponibles
LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

# Cache para loggers ya creados
_loggers = {}

def get_logger(name: str, level: str = "info") -> logging.Logger:
    """
    Obtiene un logger configurado para el módulo especificado.
    El logger se devuelve con el nombre _logger para seguir la convención solicitada.
    
    Args:
        name (str): Nombre del módulo para el logger (normalmente __name__)
        level (str, opcional): Nivel de log por defecto. Por defecto "info".
            Opciones válidas: "debug", "info", "warning", "error", "critical"
    
    Returns:
        logging.Logger: Logger configurado listo para usar (como _logger)
    """
    # Utilizar logger en caché si ya existe
    if name in _loggers:
        return _loggers[name]
    
    # Convertir nivel de string a constante de logging
    log_level = LEVELS.get(level.lower(), logging.INFO)
    
    # Crear y configurar el logger
    _logger = logging.getLogger(name)
    _logger.setLevel(log_level)
    
    # Evitar duplicación de handlers si el logger ya tiene handlers
    if _logger.handlers:
        return _logger
    
    # Crear formato para los logs
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        BASE_LOG_FILENAME,
        maxBytes=MAX_LOG_SIZE_BYTES,
        backupCount=BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
    
    # También creamos logs específicos por nivel
    _add_level_specific_handlers(_logger, formatter)
    
    # Cachear el logger creado
    _loggers[name] = _logger
    return _logger

def _add_level_specific_handlers(logger: logging.Logger, formatter: logging.Formatter) -> None:
    """
    Añade handlers específicos para cada nivel de log.
    
    Args:
        logger (logging.Logger): Logger al que añadir los handlers
        formatter (logging.Formatter): Formateador a usar en los handlers
    """
    # Crear un handler de archivo para cada nivel de log
    for level_name, level_value in LEVELS.items():
        # Nombre de archivo específico para el nivel
        level_filename = os.path.join(LOG_DIR, f"nueva_app_reflex.{level_name}.log")
        
        # Handler para este nivel específico
        level_handler = RotatingFileHandler(
            level_filename,
            maxBytes=MAX_LOG_SIZE_BYTES,
            backupCount=BACKUP_COUNT
        )
        level_handler.setLevel(level_value)
        level_handler.setFormatter(formatter)
        
        # Filtro para asegurar que solo los mensajes de este nivel van a este archivo
        level_filter = _LevelFilter(level_value)
        level_handler.addFilter(level_filter)
        
        logger.addHandler(level_handler)

class _LevelFilter(logging.Filter):
    """Filtro para mensajes de log en un nivel específico."""
    
    def __init__(self, level: int):
        """
        Inicializa el filtro con un nivel específico.
        
        Args:
            level (int): Nivel de logging a filtrar
        """
        super().__init__()
        self.level = level
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filtra los registros de log.
        
        Args:
            record (logging.LogRecord): Registro de log a evaluar
            
        Returns:
            bool: True si el registro tiene exactamente el nivel configurado
        """
        return record.levelno == self.level
