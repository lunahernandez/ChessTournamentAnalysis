# Utiliza una imagen base que tenga Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /mnt/python

# Copia los archivos Python al contenedor
COPY . /mnt/python

# Instala pymongo para conectar con MongoDB desde Python
RUN pip install pymongo

# Comando por defecto al iniciar el contenedor (esto ejecutará el script Python)
CMD ["python", "/mnt/python/create_collections.py"]
