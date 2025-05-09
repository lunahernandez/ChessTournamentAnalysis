# ChessTournamentAnalysis

### moves.csv
| Campo           | Tipo         | Descripción                          |
|-----------------|--------------|--------------------------------------|
| round           | PK           | Ronda de la partida         |
| move number     | Int32        | Número de movimiento                 |
| move            | Texto        | Notación del movimiento              |
| color           | Texto        | Color del jugador que mueve          |
| evaluation      | Double       | Evaluación del motor                 |
| time            | Texto        | Tiempo en formato original           |
| time (seconds)  | Int32        | Tiempo en segundos                   |

### details.csv
| Campo           | Tipo         | Descripción                          |
|-----------------|--------------|--------------------------------------|
| round           | PK           | Ronda de la partida         |
| event           | Texto        | Nombre del evento                    |
| white           | FK FideId    | ID FIDE del jugador blanco           |
| black           | FK FideId    | ID FIDE del jugador negro            |
| ECO             | FK           | Código de apertura                   |
| result          | Texto        | Resultado de la partida              |

### players.csv
| Campo   | Tipo     | Descripción                |
|---------|----------|----------------------------|
| name    | Texto    | Nombre del jugador         |
| FideId  | PK       | ID FIDE del jugador        |
| Elo     | Int32    | ELO del jugador            |

### openings.csv
| Campo   | Tipo     | Descripción                      |
|---------|----------|----------------------------------|
| ECO     | PK       | Código de apertura (ECO)         |
| name    | Texto    | Nombre de la apertura            |



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
