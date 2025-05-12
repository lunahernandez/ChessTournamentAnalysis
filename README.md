# AnaliC(h)e(ss)mos

Aplicación personal para la asignatura **Bases de Datos No Relacionales** de la Universidad de Las Palmas de Gran Canaria. Esta herramienta permite importar y analizar torneos de ajedrez en formato PGN, almacenarlos en MongoDB y visualizar múltiples estadísticas y evaluaciones mediante una interfaz web interactiva creada con **Shiny**.

## Funcionalidades principales

- Importación de torneos desde archivos `.pgn`.
- Evaluación automática de jugadas usando el motor **Stockfish 17.1**.
- Almacenamiento flexible de datos en **MongoDB**.
- Análisis general, individual y por partida.
- Visualización de estadísticas dinámicas con **Plotly**.
- Contenedores Docker para despliegue sencillo y multiplataforma.

## Estructura del proyecto

```
chess-tournament-analysis/
├── dashboard-tips/                   # Aplicación web Shiny
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── syles.css
|   ├── utils/                       # Scripts de gráficas y insercción de datos
│   │   ├── __init__.py
│   │   ├── pgn_to_mongo.py
│   │   └── plots.py
│   └── evaluator/
│       └── stockfish                # Motor de Stockfish
├── data/                            # Archivos PGN
├── images/                          # Imagenes de la aplicación
├── python/                          # Scripts para montar la base de datos
│   ├── create_collections.py
│   ├── Dockerfile
│   └── requirements.txt
├── notebooks/                        # Notebooks de análisis
│   └── Analysis.ipynb
├── docker-compose.yml                # Configuración de los contenedores
└── README.md
```

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python](https://www.python.org/)

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/lunahernandez/ChessTournamentAnalysis.git
   cd ChessTournamentAnalysis
   ```

2. Levantar los servicios con Docker:

   ```bash
   docker-compose up --build
   ```

3. Acceder a la aplicación web:

   ```
   http://localhost:5000
   ```

## Colecciones en MongoDB

Las colecciones utilizadas en la base de datos `ChessTournamentAnalysis`, junto con los campos almacenados en cada una. Todas las colecciones (excepto `Openings`) incluyen el campo `TournamentId` como referencia al torneo al que pertenecen.

---

### Tournaments
Contiene el nombre del torneo y un identificador único asociado.

| Campo        | Tipo   | Descripción                      |
|--------------|--------|----------------------------------|
| name         | Texto  | Nombre del torneo               |

---

### Details
Guarda la información principal de cada partida.

| Campo   | Tipo        | Descripción                               |
|---------|-------------|-------------------------------------------|
| Round   | PK          | Ronda de la partida                       |
| Event   | Texto       | Nombre del evento                         |
| White   | FK FideId   | ID FIDE del jugador con blancas           |
| Black   | FK FideId   | ID FIDE del jugador con negras            |
| ECO     | FK          | Código de apertura (ECO)                  |
| OpeningName | Texto       | Nombre de la apertura                   |
| Result  | Texto       | Resultado de la partida                   |
| TournamentId | ObjectId | Referencia al torneo correspondiente   |

---

### Players
Almacena información de los jugadores.

| Campo   | Tipo   | Descripción                |
|---------|--------|----------------------------|
| Name    | Texto  | Nombre del jugador         |
| FideId  | PK     | ID FIDE del jugador        |
| Elo     | Int32  | ELO del jugador            |
| TournamentId | ObjectId | Referencia al torneo correspondiente |

---

### Openings
Contiene información sobre las aperturas utilizadas.

| Campo   | Tipo   | Descripción                          |
|---------|--------|--------------------------------------|
| ECO     | PK     | Código de apertura (ECO)             |
| Name    | Texto  | Nombre de la apertura                |

---

### Moves
Incluye los movimientos realizados durante cada partida y sus evaluaciones.

| Campo          | Tipo     | Descripción                                     |
|----------------|----------|-------------------------------------------------|
| Round          | PK       | Ronda de la partida                             |
| Move Number    | Int32    | Número de movimiento                            |
| Move           | Texto    | Notación del movimiento                         |
| Color          | Texto    | Color del jugador que realiza el movimiento     |
| Evaluation     | Double   | Evaluación del motor (Stockfish)                |
| Time           | Texto    | Tiempo en formato original                      |
| Time (seconds) | Int32    | Tiempo convertido a segundos                     |
| TournamentId   | ObjectId | Referencia al torneo correspondiente            |
| GameId        | ObjectId | Referencia a la partida (Details)         |


---

## Pestañas de análisis

- **General:** Estadísticas de resultados, aperturas y evaluaciones.
- **Individual:** Rendimiento de cada jugador.
- **Partidas:** Visualización detallada de partidas y sus evaluaciones.
- **Importador PGN:** Carga de nuevos torneos con análisis automático.

## Trabajo futuro

- Control de duplicación de torneos.
- Mejora del diseño de la pestaña de importación.
- Filtros más precisos en búsquedas (por ronda, jugador, etc.).
- Visualización de listado de partidas por jugador.

## Autores

- Desarrollado por: **Luna Yue Hernández Guerra** y **Jorge Lorenzo Lorenzo**
