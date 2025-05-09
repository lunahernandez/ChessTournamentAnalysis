import pandas as pd
import numpy as np
import re
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from datetime import timedelta


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
            "White_Score": white_wins + white_draws * 0.5,
            "Black_Score": black_wins + black_draws * 0.5
        })

    players_stats = pd.DataFrame(stats_list)
    players_stats["Total Score"] = players_stats["White_Score"] + players_stats["Black_Score"]
    players_stats = players_stats.sort_values(by="Total Score", ascending=False)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=players_stats["Player"],
        y=players_stats["White_Score"],
        name="Puntuación con Blancas",
        marker_color="white",
        text=players_stats.apply(lambda row: f"{row['Player']}<br>Blancas: {row['White_Score']:.1f}", axis=1),
        hovertemplate="%{text}<extra></extra>",
        textposition="none"
    ))

    fig.add_trace(go.Bar(
        x=players_stats["Player"],
        y=players_stats["Black_Score"],
        name="Puntuación con Negras",
        marker_color="black",
        text=players_stats.apply(lambda row: f"{row['Player']}<br>Negras: {row['Black_Score']:.1f}", axis=1),
        hovertemplate="%{text}<extra></extra>",
        textposition="none"
    ))

    fig.update_layout(
        barmode="stack",
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
        stats_list.append({
            "Player": player,
            "Wins with White": white_wins,
            "Wins with Black": black_wins
        })

    players_stats = pd.DataFrame(stats_list)
    players_stats["Total Wins"] = players_stats["Wins with White"] + players_stats["Wins with Black"]
    players_stats = players_stats.sort_values(by="Total Wins", ascending=False)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=players_stats["Player"],
        y=players_stats["Wins with White"],
        name="Victorias con Blancas",
        marker_color="white",
        text=players_stats.apply(lambda row: f"{row['Player']}<br>Blancas: {row['Wins with White']}", axis=1),
        hovertemplate="%{text}<extra></extra>",
        textposition="none"
    ))

    fig.add_trace(go.Bar(
        x=players_stats["Player"],
        y=players_stats["Wins with Black"],
        name="Victorias con Negras",
        marker_color="black",
        text=players_stats.apply(lambda row: f"{row['Player']}<br>Negras: {row['Wins with Black']}", axis=1),
        hovertemplate="%{text}<extra></extra>",
        textposition="none"
    ))

    fig.update_layout(
        barmode="stack",
        xaxis_title="Jugador",
        yaxis_title="Partidas Ganadas",
        xaxis_tickangle=-45,
        template="ggplot2",
        showlegend=False
    )

    graph_html = pio.to_html(fig, full_html=False)
    return graph_html

def opening_effect(details_df):
    top_openings = details_df["OpeningName"].value_counts().head(10).index
    filtered_df = details_df[details_df["OpeningName"].isin(top_openings)]

    results = []
    for opening in top_openings:
        games = filtered_df[filtered_df["OpeningName"] == opening]
        eco = games["ECO"].iloc[0] if not games.empty else "N/A"
        label = f"{eco} - {opening}"

        results.append({
            "ECO": eco,
            "Tooltip": label,
            "White Wins": (games["Result"] == "1-0").sum(),
            "Black Wins": (games["Result"] == "0-1").sum(),
            "Draws": (games["Result"] == "1/2-1/2").sum()
        })

    results_df = pd.DataFrame(results)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=results_df['ECO'],
        y=results_df['White Wins'],
        name="Victorias con Blancas",
        marker_color="white",
        text=results_df['Tooltip'],
        textposition="none",
        hovertemplate="<b>%{text}</b><br>Victorias Blancas: %{y}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=results_df['ECO'],
        y=results_df['Black Wins'],
        name="Victorias con Negras",
        marker_color="black",
        text=results_df['Tooltip'],
        textposition="none",
        hovertemplate="<b>%{text}</b><br>Victorias Negras: %{y}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=results_df['ECO'],
        y=results_df['Draws'],
        name="Empates",
        marker_color="gray",
        text=results_df['Tooltip'],
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



def player_color_advantage(player_name, details_df):
    white_games = details_df[details_df["White_Player"] == player_name]
    black_games = details_df[details_df["Black_Player"] == player_name]
    
    white_wins = (white_games["Result"] == "1-0").sum()
    white_losses = (white_games["Result"] == "0-1").sum()
    white_draws = (white_games["Result"] == "1/2-1/2").sum()
    
    black_wins = (black_games["Result"] == "0-1").sum()
    black_losses = (black_games["Result"] == "1-0").sum()
    black_draws = (black_games["Result"] == "1/2-1/2").sum()

    labels = ["Victorias", "Empates", "Derrotas"]
    colors = ["#00CD00", "#FFFF00", "#CD3700"]

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
    if white_games.empty:
        fig_white =  None
    elif black_games.empty:
        fig_black =  None
    
    return fig_white, fig_black

def get_player_info(player_name, details_df):
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



def engine_evaluation(round_number, moves_df, show_colors=True):
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
import plotly.express as px
from datetime import timedelta

def plot_player_times(round_number, moves_df):
    game_moves = moves_df[moves_df["Round"] == round_number].copy()

    color_map = {"White": "white", "Black": "black"}

    game_moves["Time (formatted)"] = game_moves["Time (seconds)"].apply(
        lambda x: str(timedelta(seconds=x))
    )
    game_moves["Jugador"] = game_moves["Color"].replace({"White": "Blancas", "Black": "Negras"})

    time_interval = 1200
    max_time = game_moves["Time (seconds)"].max()
    tick_vals = list(range(0, int(max_time) + 1, time_interval))
    tick_labels = [str(timedelta(seconds=t)) for t in tick_vals]

    fig = px.line(
        game_moves,
        x="Move Number",
        y="Time (seconds)",
        color="Color",
        color_discrete_map=color_map,
        markers=True
    )

    fig.update_traces(
        marker=dict(
            size=8,
            line=dict(width=1, color="black")
        ),
        hovertemplate=(
            "<b>Jugador:</b> %{customdata[0]}<br>"
            "<b>Jugada:</b> %{x}<br>"
            "<b>Tiempo restante:</b> %{customdata[1]}<extra></extra>"
        ),
        customdata=game_moves[["Jugador", "Time (formatted)"]].values
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

    game_moves["Tiempo Diferencia Abs"] = game_moves["Time Difference"].abs()
    game_moves["Tiempo Diferencia (mm:ss)"] = game_moves["Tiempo Diferencia Abs"].apply(format_time)

    tick_values = np.linspace(game_moves["Tiempo Diferencia Abs"].min(), game_moves["Tiempo Diferencia Abs"].max(), num_ticks)
    tick_labels = [format_time(tick) for tick in tick_values]
    

    fig = px.scatter(
        game_moves,
        x="Tiempo Diferencia Abs",
        y="Eval Change",
        color="Color",
        hover_data={"Tiempo Diferencia (mm:ss)": True, "Tiempo Diferencia Abs": False},
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
            tickvals=tick_values.tolist(),
            ticktext=tick_labels,
            title="Tiempo Empleado en la Jugada (mm:ss)"
        )
    )

    fig.update_traces(
        marker=dict(
            size=8,
            line=dict(width=1, color="black")
        ),
        showlegend=False
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


def create_chess_heatmap_plotly(moves_df, round_number, color):
    game_moves = moves_df[(moves_df["Round"] == round_number) & (moves_df["Color"] == color)].copy()

    files = 'abcdefgh'
    ranks = '12345678'

    board = np.zeros((8, 8), dtype=int)

    for move in game_moves['Move'].dropna():
        matches = re.findall(r'[a-h][1-8]', move)
        if not matches:
            continue
        to_square = matches[-1]
        file = to_square[0]
        rank = to_square[1]

        row = 8 - int(rank)
        col = files.index(file)
        board[row, col] += 1

    fig = go.Figure(data=go.Heatmap(
        z=board,
        x=list(files),
        y=list(reversed(ranks)),
        colorscale='YlOrRd',
        hoverongaps=False,
        showscale=False,
        hovertemplate='%{x}%{y}<br>Movimientos: %{z}<extra></extra>'
    ))


    shapes = []
    for i in range(8):
        for j in range(8):
            shapes.append(dict(
                type="rect",
                x0=j - 0.5,
                y0=i - 0.5,
                x1=j + 0.5,
                y1=i + 0.5,
                line=dict(color="black", width=1),
                layer="above",
            ))

    fig.update_layout(
        xaxis_title='Columna',
        yaxis_title='Fila',
        yaxis_autorange='reversed',
        width=450,
        height=450,
        shapes=shapes,
    )

    return fig