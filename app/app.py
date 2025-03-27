import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from shiny import App, ui, render
from pymongo import MongoClient

# Conexión a MongoDB
client = MongoClient("mongodb://admin:password@localhost:27017/")
db = client["ChessTournamentAnalysis"]

# Cargar los jugadores desde la base de datos
players_df = pd.DataFrame(list(db["Players"].find()))
details_df = pd.DataFrame(list(db["Details"].find()))
openings_df = pd.DataFrame(list(db["Openings"].find()))

# Eliminar duplicados en players_df
players_df = players_df.drop_duplicates(subset=["FideId"])

# Realizar el merge para los jugadores de blancas
details_df = details_df.merge(players_df[['FideId', 'Name', 'Elo']], 
                               left_on="White", right_on="FideId")
details_df = details_df.rename(columns={
    "Name": "White_Player",
    "Elo": "White_Elo",
    "White": "White_Fide_ID"
})
details_df = details_df.drop(columns=['FideId'])

# Realizar el merge para los jugadores de negras
details_df = details_df.merge(players_df[['FideId', 'Name', 'Elo']], 
                               left_on="Black", right_on="FideId")
details_df = details_df.rename(columns={
    "Name": "Black_Player",
    "Elo": "Black_Elo",
    "Black": "Black_Fide_ID"
})
details_df = details_df.drop(columns=['FideId'])

# Realizar el merge con la tabla de aperturas
details_df = details_df.merge(openings_df, on="ECO", how="left")
details_df = details_df.rename(columns={"Name": "Opening_Name"})

# Función para comparar el rendimiento de los jugadores y generar el gráfico interactivo con Plotly
def players_performance_comparison(details_df):
    players = pd.concat([details_df["White_Player"], details_df["Black_Player"]]).unique()
    stats_list = []

    for player in players:
        white_wins = ((details_df["White_Player"] == player) & (details_df["Result"] == "1-0")).sum()
        white_draws = ((details_df["White_Player"] == player) & (details_df["Result"] == "1/2-1/2")).sum()
        black_wins = ((details_df["Black_Player"] == player) & (details_df["Result"] == "0-1")).sum()
        black_draws = ((details_df["Black_Player"] == player) & (details_df["Result"] == "1/2-1/2")).sum()

        stats_list.append({
            "Player": player,
            "Wins with White": white_wins + white_draws * 0.5,
            "Wins with Black": black_wins + black_draws * 0.5
        })

    players_stats = pd.DataFrame(stats_list)
    players_stats["Total Score"] = players_stats["Wins with White"] + players_stats["Wins with Black"]
    players_stats = players_stats.sort_values(by="Total Score", ascending=False)

    # Crear el gráfico interactivo con Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=players_stats["Player"],
        y=players_stats["Wins with White"],
        name="Puntuación con Blancas",
        marker_color="white",
        text=players_stats["Wins with White"],
        textposition="none",
        hoverinfo="text"
    ))

    fig.add_trace(go.Bar(
        x=players_stats["Player"],
        y=players_stats["Wins with Black"],
        name="Puntuación con Negras",
        marker_color="black",
        text=players_stats["Wins with Black"],
        textposition="none",
        hoverinfo="text"
    ))

    fig.update_layout(
        xaxis_title="Jugador",
        yaxis_title="Puntuación Obtenida",
        barmode="stack",
        xaxis_tickangle=-45,
        template="ggplot2",
        height=400,
        width=600
    )

    # Convertir el gráfico a formato HTML
    graph_html = pio.to_html(fig, full_html=False)
    return graph_html

# Definir la interfaz de usuario con pestañas
app_ui = ui.page_fluid(
    ui.h2("Chess Tournament Analysis | Cerrado IM Barcelona Junio 2024"),
    
    # Creación de pestañas
    ui.navset_tab(
        ui.nav_panel("General",  
            ui.h3("Comparación de Puntuación por Jugador"),
            ui.output_ui("output_graph")  # Mostrar el gráfico interactivo
        ),
        ui.nav_panel("Individual",  
            ui.h3("Análisis Individual"),
            ui.input_select("player", "Selecciona un jugador:", {name: name for name in players_df["Name"].tolist()}),
            ui.output_text("output_individual")
        )
    )
)

# Lógica del servidor
def server(input, output, session):
    @output
    @render.ui
    def output_graph():
        graph_html = players_performance_comparison(details_df)  # Generar el gráfico interactivo
        return ui.HTML(graph_html)  # Devolver el gráfico en formato HTML

    @output
    @render.text
    def output_individual():
        return f"Jugador seleccionado: {input.player()}"

# Crear la aplicación
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
