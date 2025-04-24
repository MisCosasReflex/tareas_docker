# Usa la última versión estable de Python
FROM python:3.12-slim

# Instala utilidades necesarias
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia dependencias e instala
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copia todo el proyecto (incluye rxconfig.py y app/) para usar la plantilla generada localmente
COPY . .

# Añade Bun y actualiza el PATH para Bun
RUN curl -fsSL https://bun.sh/install | bash && \
    export BUN_INSTALL="/root/.bun" && \
    export PATH="$BUN_INSTALL/bin:$PATH"
ENV PATH="/root/.bun/bin:$PATH"

# Cambia el directorio de trabajo para que rxconfig.py esté en /app si es necesario
WORKDIR /app

# Limpia archivos generados por Reflex y Python
RUN rm -rf .web __pycache__

# Asegura que el directorio web existe y tiene los permisos correctos
RUN mkdir -p .web && chmod -R 777 .web
# Asegura que el directorio de la base de datos existe y tiene permisos
RUN mkdir -p /app/data && chmod 777 /app/data

# Expone los puertos de Reflex
EXPOSE 3000 3100

# Comando para iniciar Reflex con configuración explícita
CMD ["reflex", "run", "--env", "dev", "--backend-host", "0.0.0.0"]
