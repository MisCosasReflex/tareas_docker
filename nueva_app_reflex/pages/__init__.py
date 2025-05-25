"""
Módulo de páginas para la aplicación Reflex.

Este módulo importa todas las páginas de la aplicación para que
estén disponibles para el enrutador de Reflex.
"""

# Páginas de gestión de usuarios
from nueva_app_reflex.pages.consultar_usuarios import consultar_usuarios
from nueva_app_reflex.pages.eliminar_usuario import page_eliminar_usuario
from nueva_app_reflex.pages.registro_usuario import registro_usuario

# Páginas de autenticación
from nueva_app_reflex.pages.login import login
from nueva_app_reflex.pages.register import register
from nueva_app_reflex.pages.profile import profile
from nueva_app_reflex.pages.change_password import change_password