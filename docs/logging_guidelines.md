# Guía de Uso del Sistema de Logs en la Aplicación Reflex

Este documento describe las mejores prácticas para utilizar el sistema de logs implementado en la aplicación.

## Estructura del Sistema de Logs

El sistema de logs está configurado para:

1. Registrar mensajes en la consola para desarrollo
2. Almacenar todos los logs en un archivo principal rotativo (`logs/nueva_app_reflex.log`)
3. Almacenar logs específicos por nivel en archivos separados:
   - `logs/nueva_app_reflex.debug.log`
   - `logs/nueva_app_reflex.info.log`
   - `logs/nueva_app_reflex.warning.log`
   - `logs/nueva_app_reflex.error.log`
   - `logs/nueva_app_reflex.critical.log`

Todos los archivos de log tienen rotación automática, manteniendo hasta 5 archivos históricos y un tamaño máximo de 10MB por archivo.

## Cómo Usar el Sistema de Logs

### Importación y Configuración

Para usar el sistema de logs en cualquier módulo:

```python
from nueva_app_reflex.utils.logger import get_logger

# Obtener un logger para el módulo actual
_logger = get_logger(__name__)

# También se puede especificar el nivel
# _logger = get_logger(__name__, level="debug")
```

### Niveles de Log y Cuándo Usarlos

1. **DEBUG**: Información detallada, útil para depuración.
   ```python
_logger.debug("Valor de variable x: {}".format(x))
   ```

2. **INFO**: Confirmación de que las cosas funcionan según lo esperado.
   ```python
_logger.info("Usuario autenticado correctamente")
   ```

3. **WARNING**: Indicación de que algo inesperado ha ocurrido, o advertencia sobre cambios futuros.
   ```python
_logger.warning("La sesión expirará en 5 minutos")
   ```

4. **ERROR**: Errores que permiten que la aplicación siga funcionando.
   ```python
_logger.error("No se pudo conectar a la base de datos: {}".format(str(e)))
   ```

5. **CRITICAL**: Errores graves que podrían causar que la aplicación deje de funcionar.
   ```python
_logger.critical("Error crítico en el sistema, reinicio necesario")
   ```

### Mejores Prácticas

1. **Nombre de Logger**: Usa siempre `__name__` como nombre del logger para que refleje la jerarquía del módulo.

2. **Estructuración de Mensajes**: 
   - Los mensajes deben ser claros y descriptivos
   - Incluye valores relevantes de variables o parámetros
   - No incluyas información sensible como contraseñas o tokens

3. **Excepción Completa**: Para errores, usa el parámetro `exc_info=True` o el método `_logger.exception()` para incluir el stack trace completo:
   ```python
   try:
       # Código que puede fallar
   except Exception as e:
       _logger.exception("Error al procesar la solicitud")
   ```

4. **Reemplazar Prints**: Reemplaza todos los `print()` por llamadas apropiadas al logger.

5. **Nivel Apropiado**: Selecciona el nivel de log adecuado según la gravedad del mensaje.

## Estructura del Formato de Log

Cada línea de log incluye:
- Fecha y hora (`%Y-%m-%d %H:%M:%S`)
- Nivel del log (`[INFO]`, `[ERROR]`, etc.)
- Nombre del logger (módulo)
- Archivo y número de línea
- Mensaje del log

Ejemplo: `2025-05-10 16:00:00 [INFO] nueva_app_reflex.state (state.py:45): Estado actualizado correctamente`

## Integración en Distintas Partes de la Aplicación

### En Servicios

```python
from nueva_app_reflex.utils.logger import get_logger

def servicio_registrar_usuario(...):
    _logger = get_logger(__name__)
    _logger.info(f"Intentando registrar usuario: {nombre}")
    
    try:
        # Código existente
        _logger.debug(f"Usuario validado: {usuario.nombre}")
        # ...
        _logger.info(f"Usuario '{usuario.nombre}' creado con éxito")
        return f"Usuario '{usuario.nombre}' creado con éxito."
    except IntegrityError:
        _logger.warning(f"Intento de crear usuario duplicado: {usuario.nombre}")
        return f"El usuario '{usuario.nombre}' o el email '{usuario.email}' ya existen."
    except Exception as e:
        _logger.error(f"Error al crear usuario: {e}", exc_info=True)
        return f"Error al crear usuario: {e}"
```

### En State de Reflex

```python
class State(rx.State):
    def __init__(self):
        super().__init__()
        self._logger = get_logger(__name__)
        
    def consultar_usuarios(self) -> None:
        self._logger.info("Iniciando consulta de usuarios")
        self.usuarios_lista, self.mensaje_usuario = servicio_consultar_usuarios()
        self._logger.debug(f"Consulta finalizada, {len(self.usuarios_lista)} usuarios encontrados")
```

## Monitoreo y Gestión de Logs

- Revisa regularmente los archivos de log para detectar patrones de error
- Considera implementar herramientas de análisis de logs en etapas futuras
- Establece una política de retención de logs según necesidades de la organización
