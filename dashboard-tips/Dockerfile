# Usa una imagen base que tenga Python
FROM python:3.9-slim

# Configura el directorio de trabajo
WORKDIR /app

# Copia los archivos de la aplicación a la imagen
COPY . /app

COPY ./evaluator/stockfish /usr/local/bin/stockfish
RUN chmod +rwx /usr/local/bin/stockfish


# Instala las dependencias de la aplicación
RUN pip install -r /app/requirements.txt

# Expone el puerto donde estará escuchando la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["shiny", "run", "--host", "0.0.0.0", "--port", "5000", "--reload", "app.py"]

