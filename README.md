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

## Cómo ejecutar
A continuación, se describen los pasos que se deben llevar a cabo para montar el servicio.
1. Descargar el fichero PGN correspondiente a un torneo retransmitido en la plataforma Lichess que contenga el tiempo por jugada.
2. Montar la base de datos y el servicio web con el comando siguiente:
```bash
docker compose up --build -d
```
3. Añadir los datos a la base de datos con la siguiente orden:
```bash
python pgn_to_mongo.py \<ruta_al_pgn\> -n \<nombre_del_torneo\> 
```
4. Acceder a [localhost:5000](http://localhost:5000/)

> Nota: Actualmente es necesario cambiar la ruta al motor de ajedrez en `pgn_to_mongo.py`
