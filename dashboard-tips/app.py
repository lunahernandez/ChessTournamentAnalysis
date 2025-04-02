from shiny import App, render, ui
from pymongo import MongoClient
from pathlib import Path
import faicons as fa
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
from datetime import timedelta
import numpy as np

client = MongoClient("mongodb://admin:password@mongodb:27017/")
db = client["ChessTournamentAnalysis"]
app_dir = Path(__file__).parent

players_df = pd.DataFrame(list(db["Players"].find()))
details_df = pd.DataFrame(list(db["Details"].find()))
openings_df = pd.DataFrame(list(db["Openings"].find()))
moves_df = pd.DataFrame(list(db["Moves"].find()))
moves_df = moves_df.merge(details_df[['Round', 'Event']], on='Round', how='left')
players_df = players_df.drop_duplicates(subset=["FideId"])

details_df = details_df.merge(players_df[['FideId', 'Name', 'Elo']], left_on="White", right_on="FideId")
details_df = details_df.rename(columns={"Name": "White_Player", "Elo": "White_Elo", "White": "White_Fide_ID"})
details_df = details_df.drop(columns=['FideId'])
details_df = details_df.merge(players_df[['FideId', 'Name', 'Elo']], left_on="Black", right_on="FideId")
details_df = details_df.rename(columns={"Name": "Black_Player", "Elo": "Black_Elo", "Black": "Black_Fide_ID"})
details_df = details_df.drop(columns=['FideId'])
details_df = details_df.merge(openings_df, on="ECO", how="left")
details_df = details_df.rename(columns={"Name": "Opening_Name"})

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

    fig = go.Figure()
    fig.add_trace(go.Bar(x=players_stats["Player"], y=players_stats["Wins with White"], name="Puntuación con Blancas", marker_color="white", text=players_stats["Wins with White"], textposition="none", hoverinfo="text"))
    fig.add_trace(go.Bar(x=players_stats["Player"], y=players_stats["Wins with Black"], name="Puntuación con Negras", marker_color="black", text=players_stats["Wins with Black"], textposition="none", hoverinfo="text"))

    fig.update_layout(
        barmode="stack",
        title="Comparación de Puntuación Obtenida por Jugador",
        xaxis_title="Jugador",
        yaxis_title="Puntuación Obtenida",
        xaxis_tickangle=-45,
        template="ggplot2",
        showlegend=False
    )

    graph_html = pio.to_html(fig, full_html=False)
    return graph_html

def players_wins_comparison(details_df):
    players = pd.concat([details_df["White_Player"], details_df["Black_Player"]]).unique()
    stats_list = []
    for player in players:
        white_wins = ((details_df["White_Player"] == player) & (details_df["Result"] == "1-0")).sum()
        black_wins = ((details_df["Black_Player"] == player) & (details_df["Result"] == "0-1")).sum()

        stats_list.append({"Player": player, "Wins with White": white_wins, "Wins with Black": black_wins})

    players_stats = pd.DataFrame(stats_list)
    players_stats["Total Wins"] = players_stats["Wins with White"] + players_stats["Wins with Black"]
    players_stats = players_stats.sort_values(by="Total Wins", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=players_stats["Player"], y=players_stats["Wins with White"], name="Victorias con Blancas", marker_color="white", text=players_stats["Wins with White"], textposition="none", hoverinfo="text"))
    fig.add_trace(go.Bar(x=players_stats["Player"], y=players_stats["Wins with Black"], name="Victorias con Negras", marker_color="black", text=players_stats["Wins with Black"], textposition="none", hoverinfo="text"))

    fig.update_layout(
        barmode="stack",
        title="Comparación de Victorias por Jugador",
        xaxis_title="Jugador",
        yaxis_title="Partidas Ganadas",
        xaxis_tickangle=-45,
        template="ggplot2",
        showlegend=False
    )

    graph_html = pio.to_html(fig, full_html=False)
    return graph_html

def opening_effect(details_df):
    opening_counts = details_df["Opening_Name"].value_counts().head(10)
    
    white_wins = []
    black_wins = []
    draws = []
    eco_codes = []
    opening_names = []

    for opening in opening_counts.index:
        opening_games = details_df[details_df["Opening_Name"] == opening]
        
        white_win_count = (opening_games["Result"] == "1-0").sum()
        black_win_count = (opening_games["Result"] == "0-1").sum()
        draw_count = (opening_games["Result"] == "1/2-1/2").sum()
        
        eco_code = opening_games["ECO"].iloc[0]  
        opening_name = opening

        white_wins.append(white_win_count)
        black_wins.append(black_win_count)
        draws.append(draw_count)
        eco_codes.append(eco_code)
        opening_names.append(opening_name)
    
    results_df = pd.DataFrame({
        'ECO': eco_codes,  
        'Opening': opening_names,
        'White Wins': white_wins,
        'Black Wins': black_wins,
        'Draws': draws
    })
    
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=results_df['ECO'],  
        y=results_df['White Wins'], 
        name="Victorias con Blancas", 
        marker_color="white", 
        text=results_df['Opening'],
        textposition="none",
        hovertemplate="<b>%{text}</b><br>Victorias Blancas: %{y}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=results_df['ECO'],  
        y=results_df['Black Wins'], 
        name="Victorias con Negras", 
        marker_color="black", 
        text=results_df['Opening'],  
        textposition="none",
        hovertemplate="<b>%{text}</b><br>Victorias Negras: %{y}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=results_df['ECO'],  
        y=results_df['Draws'], 
        name="Empates", 
        marker_color="gray", 
        text=results_df['Opening'],  
        textposition="none",
        hovertemplate="<b>%{text}</b><br>Empates: %{y}<extra></extra>"
    ))

    fig.update_layout(
        barmode="stack",
        xaxis_title="Código ECO",
        yaxis_title="Número de Partidas",
        template="ggplot2",
        showlegend=True
    )

    return fig




def player_color_advantage(player_name):
    white_games = details_df[details_df["White_Player"] == player_name]
    black_games = details_df[details_df["Black_Player"] == player_name]
    
    white_wins = (white_games["Result"] == "1-0").sum()
    white_losses = (white_games["Result"] == "0-1").sum()
    white_draws = (white_games["Result"] == "1/2-1/2").sum()
    
    black_wins = (black_games["Result"] == "0-1").sum()
    black_losses = (black_games["Result"] == "1-0").sum()
    black_draws = (black_games["Result"] == "1/2-1/2").sum()

    labels = ["Victorias", "Empates", "Derrotas"]
    colors = ["#00FF00", "#FFFF66", "#FF0000"]

    fig_white = go.Figure()
    fig_white.add_trace(go.Pie(
        labels=labels, 
        values=[white_wins, white_draws, white_losses], 
        marker=dict(colors=colors),
        textinfo="label+percent",
        hole=0.4
    ))

    fig_black = go.Figure()
    fig_black.add_trace(go.Pie(
        labels=labels, 
        values=[black_wins, black_draws, black_losses], 
        marker=dict(colors=colors),
        textinfo="label+percent",
        hole=0.4
    ))

    return fig_white, fig_black

def get_player_info(player_name):
    player_info = details_df[
        (details_df["White_Player"] == player_name) | (details_df["Black_Player"] == player_name)
    ]
    
    if not player_info.empty:
        player_elo = player_info.iloc[0]["White_Elo"] if "White_Elo" in player_info else "Desconocido"
        fide_id = player_info.iloc[0]["White_Fide_ID"] if "White_Fide_ID" in player_info else "No disponible"
    else:
        player_elo = "Desconocido"
        fide_id = "No disponible"
    
    return player_elo, fide_id



def engine_evaluation(round_number, show_colors=True):
    game_moves = moves_df[moves_df["Round"] == round_number].copy()
    if game_moves.empty:
        return go.Figure()

    game_moves["Color Order"] = game_moves["Color"].map({"White": 0, "Black": 1})
    game_moves = game_moves.sort_values(by=["Move Number", "Color Order"]).drop(columns=["Color Order"])
    game_moves["Adjusted Move Number"] = game_moves["Move Number"] + game_moves["Color"].map({"White": 0, "Black": 0.5})

    move_numbers = game_moves["Adjusted Move Number"]
    evaluations = game_moves["Evaluation"]

    def categorize_eval(eval_value):
        if eval_value >= 1.6:
            return "Decisiva Mejor", "white"
        elif eval_value >= 0.7:
            return "Clara Mejor", "white"
        elif eval_value >= 0.3:
            return "Ligera Mejor", "white"
        elif eval_value > -0.3:
            return "Igualdad", "gray"
        elif eval_value >= -0.69:
            return "Ligera Peor", "black"
        elif eval_value >= -1.59:
            return "Clara Peor", "black"
        else:
            return "Decisiva Peor", "black"

    game_moves[["Evaluation Category", "Advantage Color"]] = game_moves["Evaluation"].apply(lambda x: pd.Series(categorize_eval(x)))


    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=move_numbers,
        y=evaluations,
        mode='lines+markers',
        line=dict(color='gray', width=2),
        marker=dict(size=8, color=game_moves["Advantage Color"], line=dict(width=1, color='black')),
        name="",
        hovertemplate="<b>Jugada:</b> %{x}<br>"
                      "<b>Evaluación:</b> %{y}<br>"
                      "<b>Estado:</b> %{customdata[0]}<br>"
                      "<b>Jugador:</b> %{customdata[1]}",
        customdata=list(zip(game_moves["Evaluation Category"], game_moves["Color"])),
        showlegend=False
    ))

    fig.add_shape(
        type="line", x0=0, x1=max(move_numbers), y0=0, y1=0,
        line=dict(color="black", width=2, dash="dash")
    )

    fig.update_layout(
        xaxis_title="Número de Jugada",
        yaxis_title="Evaluación",
        template="ggplot2",
        legend_title="Estado de la Evaluación"
    )

    return fig

def plot_player_times(round_number):
    game_moves = moves_df[moves_df["Round"] == round_number].copy()

    color_map = {"White": "white", "Black": "black"}

    game_moves["Time (formatted)"] = game_moves["Time (seconds)"].apply(
        lambda x: str(timedelta(seconds=x))
    )

    time_interval = 1200
    max_time = game_moves["Time (seconds)"].max()
    
    tick_vals = list(range(0, int(max_time) + 1, time_interval))
    tick_labels = [str(timedelta(seconds=t)) for t in tick_vals]
    
    game_moves["Jugador"] = game_moves["Color"].replace({"White": "Blancas", "Black": "Negras"})

    fig = px.line(
        game_moves,
        x="Move Number",
        y="Time (seconds)",
        color="Color",
        color_discrete_map=color_map,
        markers=True,
        labels={"Time (formatted)": "Tiempo", "Time (seconds)": "Tiempo restante (HH:MM:ss)", 
                "Move Number": "Número de Jugada", "Color": "Jugador"},
        hover_data={
            "Time (seconds)": False,
            "Time (formatted)": True,
            "Jugador": True
        }
    )

    fig.update_traces(
        marker=dict(
            size=8,
            line=dict(width=1, color="black")
        )
    )

    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=True),
        yaxis=dict(
            showgrid=True,
            tickmode="array",
            tickvals=tick_vals,
            ticktext=tick_labels,
            ticks="outside"
        ),
        template="ggplot2"
    )

    return fig


def format_time(seconds):
    """Convierte segundos a formato mm:ss"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def time_vs_eval_change_single_game(moves_df, round_number, num_ticks=10):
    game_moves = moves_df[moves_df["Round"] == round_number].copy()

    game_moves["Time (seconds)"] = pd.to_numeric(game_moves["Time (seconds)"], errors="coerce")
    game_moves.dropna(subset=["Evaluation", "Time (seconds)"], inplace=True)

    game_moves["Time Net"] = game_moves["Time (seconds)"] - 30
    game_moves["Time Net"] = game_moves["Time Net"].apply(lambda x: max(x, 0))

    game_moves["Color Order"] = game_moves["Color"].map({"White": 0, "Black": 1})
    game_moves.sort_values(by=["Move Number", "Color Order"], inplace=True)
    game_moves.drop(columns=["Color Order"], inplace=True)

    game_moves["Time Difference"] = - (game_moves["Time Net"] - game_moves.groupby("Color")["Time (seconds)"].shift(1))
    game_moves["Eval Change"] = game_moves["Evaluation"].diff()
    game_moves.dropna(subset=["Time Difference", "Eval Change"], inplace=True)

    # Convertir tiempo a valores absolutos y aplicar formato mm:ss
    game_moves["Tiempo Diferencia Abs"] = game_moves["Time Difference"].abs()
    game_moves["Tiempo Diferencia (mm:ss)"] = game_moves["Tiempo Diferencia Abs"].apply(format_time)  # Para tooltip

    # Seleccionar un número limitado de ticks en el eje X
    tick_values = np.linspace(game_moves["Tiempo Diferencia Abs"].min(), game_moves["Tiempo Diferencia Abs"].max(), num_ticks)
    tick_labels = [format_time(tick) for tick in tick_values]

    fig = px.scatter(
        game_moves,
        x="Tiempo Diferencia Abs",  # Mantener valores numéricos para ordenar
        y="Eval Change",
        color="Color",
        hover_data={"Tiempo Diferencia (mm:ss)": True, "Tiempo Diferencia Abs": False},  # Mostrar solo el formateado
        labels={
            "Tiempo Diferencia Abs": "Tiempo Neto en la Jugada (segundos)",
            "Eval Change": "Cambio en Evaluación",
            "Color": "Color de las Piezas"
        },
        color_discrete_map={"White": "white", "Black": "black"},
        template="ggplot2"
    )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=tick_values.tolist(),  # Usar valores limitados
            ticktext=tick_labels,  # Mostrar formato mm:ss
            title="Tiempo Neto en la Jugada (mm:ss)"
        )
    )

    fig.update_traces(
        marker=dict(
            size=8,
            line=dict(width=1, color="black")
        )
    )

    fig.add_hline(y=0, line_dash="dash", line_color="black")

    return fig

def elo_vs_result(details_df):
    details_df_clean = details_df.dropna(subset=["Result"])

    details_df_clean['Result'] = details_df_clean['Result'].map({
        '1-0': 'Victoria Blancas',
        '0-1': 'Victoria Negras',
        '1/2-1/2': 'Empate'
    })

    details_df_clean = details_df_clean[['White_Elo', 'Black_Elo', 'Result']]

    min_elo = min(details_df_clean["White_Elo"].min(), details_df_clean["Black_Elo"].min())
    max_elo = max(details_df_clean["White_Elo"].max(), details_df_clean["Black_Elo"].max())

    fig = px.scatter(
        details_df_clean,
        x="White_Elo",
        y="Black_Elo",
        color="Result",
        labels={
            "White_Elo": "ELO del Jugador de Blancas",
            "Black_Elo": "ELO del Jugador de Negras",
            "Result": "Resultado"
        },
        color_discrete_map={
            "Victoria Blancas": "white",
            "Victoria Negras": "black",
            "Empate": "gray"
        },
        template="ggplot2"
    )

    fig.update_traces(
        marker=dict(
            size=8,
            line=dict(width=1, color="black")
        )
    )

    fig.add_trace(
        dict(
            type="scatter",
            x=[min_elo, max_elo],
            y=[min_elo, max_elo],
            mode="lines",
            line=dict(color="gray", dash="dash"),
            showlegend=False
        )
    )

    return fig


def categorize_stockfish_eval(eval_value, is_white):
    if not is_white:
        eval_value = -eval_value

    if eval_value >= 1.6:
        return "Decisiva Mejor"
    elif eval_value >= 0.7:
        return "Clara Mejor"
    elif eval_value >= 0.3:
        return "Ligera Mejor"
    elif eval_value > -0.3:
        return "Igualdad"
    elif eval_value >= -0.69:
        return "Ligera Peor"
    elif eval_value >= -1.59:
        return "Clara Peor"
    else:
        return "Decisiva Peor"

def evaluation_distribution_plotly(details_df, moves_df):
    merged_df = moves_df.merge(details_df, on="Round", how="left")

    merged_df["Player"] = merged_df.apply(
        lambda row: row["White_Player"] if row["Move Number"] % 2 != 0 else row["Black_Player"],
        axis=1
    )

    merged_df["Is_White"] = merged_df["Move Number"] % 2 != 0

    merged_df["Eval Category"] = merged_df.apply(
        lambda row: categorize_stockfish_eval(row["Evaluation"], row["Is_White"]),
        axis=1
    )

    eval_counts = merged_df.groupby(["Player", "Eval Category"]).size().unstack(fill_value=0)
    eval_percentage = eval_counts.div(eval_counts.sum(axis=1), axis=0) * 100

    eval_order = ["Decisiva Peor", "Clara Peor", "Ligera Peor", "Igualdad", "Ligera Mejor", "Clara Mejor", "Decisiva Mejor"]
    eval_percentage = eval_percentage[eval_order].reset_index()

    eval_data = eval_percentage.melt(id_vars="Player", var_name="Estado de la Posición", value_name="Porcentaje")

    color_map = {
        "Decisiva Peor": "#8B0000",
        "Clara Peor": "#FF0000",
        "Ligera Peor": "#FFA07A",
        "Igualdad": "#EEE9E9",
        "Ligera Mejor": "#BCE3B1",
        "Clara Mejor": "#76C95F",
        "Decisiva Mejor": "#3D6831"
    }

    fig = px.bar(
        eval_data,
        x="Player",
        y="Porcentaje",
        color="Estado de la Posición",
        labels={"Player": "Jugador"},
        color_discrete_map=color_map
    )

    fig.update_layout(
        showlegend=False,
        barmode="stack",
        xaxis_title="Jugador",
        yaxis_title="Porcentaje de Jugadas",
        xaxis_tickangle=-45
    )

    return fig



ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

app_ui = ui.page_fluid( 
    ui.h1("Chess Tournament Analysis | Cerrado IM Barcelona Junio 2024", style="text-align:left;"),
    ui.navset_tab(
        ui.nav_panel("General",  
            ui.layout_columns(
                ui.card(
                    ui.card_header("Comparación de Puntuación por Jugador"), 
                    ui.output_ui("output_graph1"), full_screen=True
                ),
                ui.card(
                    ui.card_header("Comparación de Victorias por Jugador"), 
                    ui.output_ui("output_graph2"), full_screen=True
                ),
                col_widths=[6, 6]
            ),
            ui.card(
                    ui.card_header("Comparación de Resultados por Apertura"),
                    ui.output_ui("output_graph3"), full_screen=True
                ),
                
            ui.layout_columns(
                ui.card(
                    ui.card_header("Comparación de Resultados por Jugador según el ELO"), 
                    ui.output_ui("output_graph8"), full_screen=True
                ),
                ui.card(
                    ui.card_header("Distribución de Evaluaciones por Jugador"), 
                    ui.output_ui("output_graph9"), full_screen=True
                ),
                col_widths=[6, 6]
            ),
        ),
        
        ui.nav_panel("Individual",  
            ui.page_sidebar(
                ui.sidebar(
                    ui.input_select("player", "Selecciona un jugador:", {name: name for name in players_df["Name"].tolist()}),
                    open="desktop",
                ),
                ui.layout_columns(
                    ui.output_ui("player_name_card"),
                    ui.output_ui("player_elo_card"),
                    ui.output_ui("player_fide_id_card")
                ),
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Rendimiento con blancas"),
                        ui.output_ui("output_graph4i"), full_screen=True
                    ),
                    ui.card(
                        ui.card_header("Rendimiento con negras"),
                        ui.output_ui("output_graph4ii"), full_screen=True
                    )
                ),
            ),
        ),        
 ui.nav_panel("Partidas",  
    ui.page_sidebar(
        ui.sidebar(
            ui.input_select("selected_game", "Selecciona una partida:", 
                            {game: game for game in details_df["Event"].tolist()}),
            
            ui.card(
                ui.card_header(ui.row([
                    ui.column(10, [
                        ui.HTML(f"{fa.icon_svg('user', 'solid')} Jugador Blanco")
                    ]), 
                    ui.column(2, [
                        ui.output_ui("white_player_result")
                    ])
                ])),
                ui.card_body(ui.output_ui("white_player_info")),
                style="background-color: white; color: black;"
            ),

            
            ui.card(
            ui.card_header(ui.row([
                ui.column(10, [
                    ui.HTML(f"{fa.icon_svg('user', 'solid')} Jugador Negro")
                ]), 
                ui.column(2, [
                    ui.output_ui("black_player_result")
                ])
            ])),
            ui.card_body(ui.output_ui("black_player_info")),
            style="background-color: black; color: white;"
        ),
            
            open="desktop",
        ),
        ui.card(
            ui.card_header("Evaluación del Motor por Jugada"),
            ui.output_ui("output_graph5"), full_screen=True
        ),
        ui.card(
            ui.card_header("Tiempo Restante por Jugada"),
            ui.output_ui("output_graph6"), full_screen=True
        ),
        ui.card(
            ui.card_header("Relación entre Tiempo Consumido y Cambio en Evaluación"),
            ui.output_ui("output_graph7"), full_screen=True
        )
    ),
)


    ),
    ui.include_css(app_dir / "styles.css"),
    title="Chess Tournament Analysis | Cerrado IM Barcelona Junio 2024",
    fillable=True,
)





def server(input, output, session):
    @render.ui
    def player_name_card():
        return ui.card(
            ui.card_header(ui.HTML(f"{fa.icon_svg('user', 'solid')} Nombre")),
            ui.card_body(ui.p(input.player()))
        )

    @render.ui
    def player_elo_card():
        player_elo, _ = get_player_info(input.player())
        return ui.card(
            ui.card_header(ui.HTML(f"{fa.icon_svg('chart-line')} ELO")),
            ui.card_body(ui.p(str(player_elo)))
        )

    @render.ui
    def player_fide_id_card():
        _, fide_id = get_player_info(input.player())
        return ui.card(
            ui.card_header(ui.HTML(f"{fa.icon_svg('id-card')} FIDE ID")),
            ui.card_body(ui.p(str(fide_id)))
        )
    @output
    @render.text
    def white_player_info():
        game_details = details_df[details_df["Event"] == input.selected_game()]
        if game_details.empty:
            return "No disponible"
        player_name = game_details["White_Player"].values[0]
        elo = game_details["White_Elo"].values[0]
        fide_id = game_details["White_Fide_ID"].values[0]
        return ui.HTML(f"Nombre: {player_name}<br>ELO: {elo}<br>FIDE ID: {fide_id}")

    @output
    @render.text
    def black_player_info():
        game_details = details_df[details_df["Event"] == input.selected_game()]
        if game_details.empty:
            return "No disponible"
        player_name = game_details["Black_Player"].values[0]
        elo = game_details["Black_Elo"].values[0]
        fide_id = game_details["Black_Fide_ID"].values[0]
        return ui.HTML(f"Nombre: {player_name}<br>ELO: {elo}<br>FIDE ID: {fide_id}")
    
    @render.ui
    def output_graph1():
        graph_html = players_performance_comparison(details_df)
        return ui.HTML(graph_html)
    @render.ui
    def output_graph2():
        graph_html = players_wins_comparison(details_df)
        return ui.HTML(graph_html)

    @render.ui
    def output_graph3():
        fig = opening_effect(details_df)
        return fig

    @render.ui
    def output_graph4i():
        player_name = input.player()
        fig_white, _ = player_color_advantage(player_name)
        return fig_white

    @render.ui
    def output_graph4ii():
        player_name = input.player()
        _, fig_black = player_color_advantage(player_name)
        return fig_black
    
    @render.ui
    def output_graph5():
        selected_game_id = input.selected_game()
        
        round_info = moves_df[moves_df["Event"] == selected_game_id]["Round"].unique()
        
        if len(round_info) == 0:
            return "No se encontró la ronda para esta partida."

        round_number = round_info[0]
        
        fig = engine_evaluation(round_number)
        return fig

    @render.ui
    def output_graph6():
        selected_game_id = input.selected_game()
        
        round_info = moves_df[moves_df["Event"] == selected_game_id]["Round"].unique()
        
        if len(round_info) == 0:
            return "No se encontró la ronda para esta partida."

        round_number = round_info[0]
        
        fig = plot_player_times(round_number)
        return fig
    
    @render.ui
    def output_graph7():
        selected_game_id = input.selected_game()
        
        round_info = moves_df[moves_df["Event"] == selected_game_id]["Round"].unique()
        
        if len(round_info) == 0:
            return "No se encontró la ronda para esta partida."

        round_number = round_info[0]
        
        fig = time_vs_eval_change_single_game(moves_df, round_number)
        return fig
    

    @render.ui
    def output_graph8():        
        fig = elo_vs_result(details_df)
        return fig


    @render.ui
    def output_graph9():        
        fig = evaluation_distribution_plotly(details_df, moves_df)
        return fig

    

    @output
    @render.text
    def black_player_result():
        game_details = details_df[details_df["Event"] == input.selected_game()]
        if game_details.empty:
            return "No disponible"
        
        result = game_details["Result"].values[0]
        result = result.split("-")[1]
        
        if result not in ['1', '0']:
            result = '½'
        
        return ui.HTML(f'<span style="font-size: 20px; font-weight: bold; color: white;">{result}</span>')

    @output
    @render.text
    def white_player_result():
        game_details = details_df[details_df["Event"] == input.selected_game()]
        if game_details.empty:
            return "No disponible"
        
        result = game_details["Result"].values[0]
        result = result.split("-")[0]

        if result not in ['1', '0']:
            result = '½'
        
        return ui.HTML(f'<span style="font-size: 20px; font-weight: bold; color: black;">{result}</span>')  





app = App(app_ui, server)

if __name__ == "__main__":
    app.run()