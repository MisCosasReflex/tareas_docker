# Reflex Task Manager - Dockerized

Este proyecto es una aplicación web construida con [Reflex](https://reflex.dev/) y SQLAlchemy, preparada para ejecutarse tanto en local como en Docker, siguiendo buenas prácticas de escalabilidad y portabilidad.

---

## 🚀 ¿Cómo levantar la app en Docker?

1. **Construye la imagen y levanta el contenedor:**
   ```bash
   docker compose build
   docker compose up
   ```

2. **Accede a la app:**
   - Abre tu navegador en [http://localhost:3005](http://localhost:3005)

---

## 📦 Estructura básica

- `Dockerfile`: Configuración para construir la imagen Docker.
- `docker-compose.yml`: Orquestación y mapeo de puertos.
- `requirements.txt`: Dependencias Python (incluye Reflex y SQLAlchemy).
- `rxconfig.py`: Configuración de la app Reflex.
- `nueva_app_reflex/`: Código fuente de la app.

---

## 🐳 Detalles clave de la Dockerización

- **Node.js y npm:** Se instalan explícitamente en el Dockerfile porque Reflex los requiere para compilar el frontend. En local, Reflex los descarga automáticamente si hacen falta, pero en Docker debes instalarlos tú.
- **curl y unzip:** Se instalan para permitir que Reflex descargue y descomprima binarios o plantillas durante la build.
- **Puertos:**
  - El contenedor expone el puerto 3000 (frontend Reflex) y se mapea al 3005 del host para evitar conflictos con la versión local.
- **Permisos:** El Dockerfile limpia archivos generados y ajusta permisos para evitar bloqueos en builds repetidos.

---

## 💡 Notas y recomendaciones

- Si amplías el proyecto (por ejemplo, añadiendo una base de datos externa, variables de entorno, tests, etc.), documenta aquí los pasos extra o comandos relevantes.
- Si usas Windows localmente, normalmente no necesitas instalar curl/unzip, pero en Docker (Linux) sí.
- Si cambias la estructura de carpetas, asegúrate de actualizar el Dockerfile y docker-compose.yml en consecuencia.
- Para builds de producción, revisa los permisos y considera usar imágenes más pequeñas o multi-stage.

---

## 📚 Recursos útiles
- [Reflex Docs](https://reflex.dev/docs/)
---

## ✍️ Modifica este README

Actualiza este archivo cada vez que agregues nuevas funcionalidades, dependencias, servicios o instrucciones. ¡Manténlo como tu fuente de verdad para el despliegue y desarrollo!

---

**¿Dudas o problemas?**
- Revisa los logs del contenedor con `docker compose logs reflex_app`.
- Verifica el estado con `docker compose ps`.
- Consulta la documentación oficial de Reflex o abre un issue en el repo.
