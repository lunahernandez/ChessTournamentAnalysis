# ChessTournamentAnalysis
## moves.csv
- round PK
- move number (Int32)
- move
- color
- evaluation (double)
- time
- time (seconds) (Int32)

## details.csv
- round PK
- event
- white FK FideId
- black FK FideId
- ECO FK
- result

## players.csv
- name
- FideId PK
- Elo (Int32)

## openings.csv
- ECO PK
- name

## Programas previos
Es necesario tener descargado el motor de ajedrez [Stockfish](https://stockfishchess.org/download/).

1. Se extraer el zip y se copia en una ruta que queramos para nosotros luego usarla
2. En la llamada de pgn_to_mongo.py se debe cambiar la ruta al motor de ajedrez en la variable `engine_path`.

## Cómo ejecutar
A continuación, se describen los pasos que se deben llevar a cabo para montar el servicio.
1. Descargar el fichero PGN correspondiente a un torneo retransmitido en la plataforma Lichess que contenga el tiempo por jugada.
2. Montar la base de datos y el servicio web con el comando siguiente:
```bash
docker compose up --build -d
```
3. Añadir los datos a la base de datos con la siguiente orden:
```bash
python pgn_to_mongo.py \<ruta_al_pgn\> -n \<nombre_del_torneo\> -engine_path \<ruta_al_motor_de_ajedrez\>
```
   - `\<ruta_al_pgn\>`: Ruta al fichero PGN que se ha descargado.
   - `\<nombre_del_torneo\>`: Nombre del torneo que se va a añadir a la base de datos.
   - `\<ruta_al_motor_de_ajedrez\>`: Ruta al motor de ajedrez que se ha descargado.

Ejemplo de ejecución: 
```bash
python pgn_to_mongo.py ./data/junio_2024.pgn -n "Cerrado IM Junio 2024" -e "C:/Program Files/Stockfish/stockfish-windows-x86-64-avx2.exe"

```
4. Acceder a [localhost:5000](http://localhost:5000/)

> Nota: Actualmente es necesario cambiar la ruta al motor de ajedrez en `pgn_to_mongo.py`
