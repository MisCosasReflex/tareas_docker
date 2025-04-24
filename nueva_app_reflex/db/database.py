"""
Módulo de configuración de la base de datos para la aplicación Reflex.
Utiliza SQLAlchemy con SQLite y proporciona el motor, la sesión y la creación de tablas.
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from sqlalchemy.engine import Engine

# Obtener el directorio base absoluto donde se encuentra este archivo usando Path
BASE_DIR: Path = Path(__file__).resolve().parent
# Definir la ruta absoluta para la base de datos SQLite usando Path
DB_PATH: Path = Path("/app/data/app.db")
# Construir la URL de conexión para SQLAlchemy
DATABASE_URL: str = f"sqlite:///{DB_PATH}"

# Crear el motor de la base de datos con el parámetro necesario para SQLite
engine: Engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
# Crear la clase SessionLocal para generar sesiones de base de datos
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Crear todas las tablas definidas en los modelos si no existen
Base.metadata.create_all(bind=engine)
