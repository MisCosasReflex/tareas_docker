"""
Módulo de configuración de la base de datos para la aplicación Reflex.

Este módulo configura la conexión a la base de datos SQLite usando SQLAlchemy.
Permite definir la URL de la base de datos mediante una variable de entorno o un valor por defecto.
Proporciona el motor, la clase de sesión y la creación automática de tablas.

Variables:
    DEFAULT_DB_PATH (Path): Ruta por defecto de la base de datos SQLite.
    DB_PATH (str): Ruta obtenida de la variable de entorno o por defecto.
    DATABASE_URL (str): URL de conexión para SQLAlchemy.
    engine (Engine): Motor de base de datos.
    SessionLocal (sessionmaker): Clase para crear sesiones.

Uso:
    Importar SessionLocal para obtener sesiones y operar sobre la base de datos.
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
