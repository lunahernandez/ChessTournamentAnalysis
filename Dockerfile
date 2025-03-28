# Utiliza una imagen ligera de Python
FROM python:3.9-slim

# Actualiza los repositorios e instala el cliente MongoDB
RUN apt-get update && apt-get install -y mongodb-clients

# Instala pymongo para conectar con MongoDB desde Python
RUN pip install pymongo

# Define el directorio de trabajo
WORKDIR /mnt/python

# Copia los archivos Python al contenedor
COPY ./python /mnt/python

# Copia los archivos de datos necesarios
COPY ./data /mnt/data

# Comando por defecto al iniciar el contenedor (esto ejecutará el script Python)
CMD ["python", "/mnt/python/create_collections.py"]
