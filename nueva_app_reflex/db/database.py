"""
Módulo de configuración de la base de datos para la aplicación Reflex.
Utiliza SQLAlchemy con SQLite y proporciona el motor, la sesión y la creación de tablas.
La ruta de la base de datos se puede configurar con la variable de entorno DATABASE_PATH o en el archivo .env.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from sqlalchemy.engine import Engine

# Obtener la ruta de la base de datos desde la variable de entorno o usar ruta relativa por defecto
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"
DB_PATH = os.environ.get("DATABASE_PATH", str(DEFAULT_DB_PATH))
DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"[DEBUG] Usando base de datos en: {DB_PATH}")

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
