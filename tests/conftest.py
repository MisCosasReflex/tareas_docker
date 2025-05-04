"""
Configuración global de pytest para los tests del proyecto.
Asegura que la raíz del proyecto esté en sys.path para los imports relativos.
"""
import sys
from pathlib import Path

# Añade la raíz del proyecto al sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
