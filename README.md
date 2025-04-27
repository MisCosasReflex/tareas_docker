# Reflex Task Manager - Dockerized

Este proyecto es una aplicación web construida con [Reflex](https://reflex.dev/) y SQLAlchemy, preparada para ejecutarse tanto en local como en Docker, siguiendo buenas prácticas de escalabilidad y portabilidad.

---

## ¿Cómo levantar la app en Docker?

1. **Construye la imagen y levanta el contenedor:**
   ```bash
   docker compose build
   docker compose up
   ```

2. **Accede a la app:**
   - Abre tu navegador en [http://localhost:3005](http://localhost:3005)

---

## Estructura básica

- `Dockerfile`: Configuración para construir la imagen Docker.
- `docker-compose.yml`: Orquestación y mapeo de puertos.
- `requirements.txt`: Dependencias Python (incluye Reflex y SQLAlchemy).
- `rxconfig.py`: Configuración de la app Reflex.
- `nueva_app_reflex/`: Código fuente de la app.

---

## Estructura del proyecto

```
nueva_app_reflex/
├── db/         # Código Python: modelos, schemas, configuración de la base de datos
├── data/       # Datos reales de la app: aquí se guarda la base de datos SQLite (app.db)
├── nueva_app_reflex.py  # Entrada principal de la app Reflex
├── state.py    # Lógica de estado global
└── ...
```

## Uso en desarrollo local

1. **Crea el entorno virtual y actívalo:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt  # si tienes requirements
   ```
2. **Asegúrate de que existe la carpeta `data/`:**
   ```bash
   mkdir -p data
   ```
3. **Ejecuta la app:**
   ```bash
   reflex run
   ```
   La base de datos estará en `./data/app.db`.

## Uso con Docker

1. **Construye y ejecuta el contenedor:**
   ```bash
   docker-compose up --build
   ```
2. **Persistencia de datos:**
   - El archivo de base de datos estará en `./data/app.db` en tu máquina, y en `/app/data/app.db` dentro del contenedor.
   - Puedes respaldar o inspeccionar el archivo desde tu carpeta local.

## Notas importantes

- La carpeta `data/` está en `.gitignore` para evitar subir datos reales al repositorio.
- El código de modelos, schemas y configuración está en `db/`. **No guardes archivos de datos en esa carpeta.**
- Puedes cambiar la ubicación de la base de datos usando la variable de entorno `DATABASE_PATH`.

## Recursos útiles
- [Reflex Docs](https://reflex.dev/docs/)
---

## Estado actual de la aplicación

- **Página raíz (`/`)**: Muestra un encabezado "Aplicacion de tareas por hacer" y dos botones:
    - **"Agrega un usuario nuevo"**: Dirige a la página de registro de usuario (`/registro-usuario`).
    - **"Consulta los usuarios agregados"**: (Botón preparado para futura funcionalidad de listado de usuarios).
- **Página de registro de usuario (`/registro-usuario`)**: Permite ingresar nombre, email, contraseña y marcar si el usuario es administrador. Al enviar el formulario, se muestra un mensaje de éxito (el registro real en base de datos puede activarse/restaurarse en el callback correspondiente).
- **Base de datos**: Se gestiona con SQLAlchemy y SQLite. El archivo se almacena en `data/app.db` y es persistente tanto en local como en Docker.
- **Preparado para contenedores**: Toda la configuración y rutas de base de datos son compatibles con Docker y desarrollo local.

### Flujo lógico actual
1. El usuario accede a la página principal (`/`).
2. Puede ir al registro de usuario mediante el botón correspondiente.
3. (Próximamente) Podrá consultar usuarios agregados desde el botón preparado.

> ⚠️ **Nota:** Las nuevas funcionalidades (página de registro de usuario y navegación desde la raíz) solo han sido probadas en entorno local. **Aún no se han verificado en Docker.** Si encuentras algún problema ejecutando en contenedor, revisa la configuración y dependencias, y repórtalo para su ajuste.

---

## Modifica este README

Actualiza este archivo cada vez que agregues nuevas funcionalidades, dependencias, servicios o instrucciones. ¡Manténlo como tu fuente de verdad para el despliegue y desarrollo!

---

**¿Dudas o problemas?**
- Revisa los logs del contenedor con `docker compose logs reflex_app`.
- Verifica el estado con `docker compose ps`.
- Consulta la documentación oficial de Reflex o abre un issue en el repo.
