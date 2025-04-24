# Permite que el directorio db sea tratado como un paquete de Python.
# Importa explícitamente los modelos y la sesión para facilitar el acceso desde otros módulos.
from .models import Base, Usuario, Tarea
from .database import SessionLocal, engine
