from shiny import App, render, ui
from pymongo import MongoClient
from pathlib import Path
import faicons as fa
import pandas as pd
from utils.plots import (players_performance_comparison, players_wins_comparison, 
                         opening_effect, player_color_advantage, get_player_info, 
                         engine_evaluation, plot_player_times, time_vs_eval_change_single_game,
                         elo_vs_result, evaluation_distribution_plotly, create_chess_heatmap_plotly)

from pymongo.errors import ServerSelectionTimeoutError

try:
    client = MongoClient("mongodb://admin:password@host.docker.internal:27017/")
    client.server_info()
    db = client["ChessTournamentAnalysis"]
    print("Conexión a MongoDB exitosa.")
except ServerSelectionTimeoutError as e:
    print("No se pudo conectar a MongoDB. Verifica que el contenedor esté corriendo y que la URI sea correcta.")
    print(f"Error: {e}")
    exit(1)

app_dir = Path(__file__).parent

players_df = pd.DataFrame(list(db["Players"].find()))
details_df = pd.DataFrame(list(db["Details"].find()))
openings_df = pd.DataFrame(list(db["Openings"].find()))
tournaments_df = pd.DataFrame(list(db["Tournaments"].find()))
moves_df = pd.DataFrame(list(db["Moves"].find()))
moves_df = moves_df.merge(details_df[['TournamentId', 'Round', 'Event']], on=['Round', 'TournamentId'], how='left')

players_df = players_df.drop_duplicates(subset=["FideId"])

details_df = details_df.merge(players_df[['FideId', 'Name', 'Elo']], left_on="White", right_on="FideId")
details_df = details_df.rename(columns={"Name": "White_Player", "Elo": "White_Elo", "White": "White_Fide_ID"})
details_df = details_df.drop(columns=['FideId'])
details_df = details_df.merge(players_df[['FideId', 'Name', 'Elo']], left_on="Black", right_on="FideId")
details_df = details_df.rename(columns={"Name": "Black_Player", "Elo": "Black_Elo", "Black": "Black_Fide_ID"})
details_df = details_df.drop(columns=['FideId'])
details_df = details_df.merge(openings_df, on="ECO", how="left")
details_df = details_df.rename(columns={"Name": "Opening_Name"})




ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("selected_tournament", "Selecciona un torneo:", 
                        {name: name for name in tournaments_df["Name"]}),
        open="desktop",
        title="Torneos"
    ),
    ui.page_fluid( 
    ui.output_ui("tournament_title"),
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
                    ui.output_ui("player_dropdown"),
                    open="desktop"
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
               ui.output_ui("dropdown_partidas"),
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
        ),
        ui.layout_columns(
            ui.card(
                ui.card_header("Mapa de calor de movimientos de Blancas"),
                ui.output_ui("heatmap_white"), full_screen=True
            ),
            ui.card(
                ui.card_header("Mapa de calor de movimientos de Negras"),
                ui.output_ui("heatmap_black"), full_screen=True
            ),
            col_widths=[6, 6]
        )
    ),
)


    ),
    ui.include_css(app_dir / "styles.css"),
    title="Chess Tournament Analysis | Cerrado IM Barcelona Junio 2024",
    fillable=True,
)

)




def server(input, output, session):
    @render.ui
    def tournament_title():
        selected = input.selected_tournament()
        return ui.h1(f"Chess Tournament Analysis | {selected or 'Selecciona un torneo'}", style="text-align:left;")

    @render.ui
    def player_name_card():
        return ui.card(
            ui.card_header(ui.HTML(f"{fa.icon_svg('user', 'solid')} Nombre")),
            ui.card_body(ui.p(input.player()))
        )

    @render.ui
    def player_elo_card():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        details_filtered = details_df[details_df["TournamentId"] == tournament_id]
        player_elo, _ = get_player_info(input.player(), details_filtered)
        
        return ui.card(
            ui.card_header(ui.HTML(f"{fa.icon_svg('chart-line')} ELO")),
            ui.card_body(ui.p(str(player_elo)))
        )


    @render.ui
    def player_fide_id_card():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        details = details_df[details_df["TournamentId"] == tournament_id]
        _, fide_id = get_player_info(input.player(), details)
        return ui.card(
            ui.card_header(ui.HTML(f"{fa.icon_svg('id-card')} FIDE ID")),
            ui.card_body(ui.p(str(fide_id)))
        )

    @output
    @render.text
    def white_player_info():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        selected_round = str(input.selected_game()).strip()
        game_details = details_df[
            (details_df["Round"].astype(str).str.strip() == selected_round) &
            (details_df["TournamentId"] == tournament_id)
        ]
        
        if game_details.empty:
            return "No disponible"
        
        player_name = game_details["White_Player"].values[0]
        elo = game_details["White_Elo"].values[0]
        fide_id = game_details["White_Fide_ID"].values[0]
        
        return ui.HTML(f"Nombre: {player_name}<br>ELO: {elo}<br>FIDE ID: {fide_id}")



    @output
    @render.text
    def black_player_info():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        selected_round = str(input.selected_game()).strip()
        game_details = details_df[
            (details_df["Round"].astype(str).str.strip() == selected_round) &
            (details_df["TournamentId"] == tournament_id)
        ]

        if game_details.empty:
            return "No disponible"
        player_name = game_details["Black_Player"].values[0]
        elo = game_details["Black_Elo"].values[0]
        fide_id = game_details["Black_Fide_ID"].values[0]
        return ui.HTML(f"Nombre: {player_name}<br>ELO: {elo}<br>FIDE ID: {fide_id}")
    
    @render.ui
    def output_graph1():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        details = details_df[details_df["TournamentId"] == tournament_id]
        graph_html = players_performance_comparison(details)
        return ui.HTML(graph_html)
    @render.ui
    def output_graph2():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        details = details_df[details_df["TournamentId"] == tournament_id]
        graph_html = players_wins_comparison(details)
        return ui.HTML(graph_html)

    @render.ui
    def output_graph3():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        details = details_df[details_df["TournamentId"] == tournament_id]
        fig = opening_effect(details)
        return fig

    @render.ui
    def output_graph4i():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        details = details_df[details_df["TournamentId"] == tournament_id]
        player_name = input.player()
        fig_white, _ = player_color_advantage(player_name, details)
        return fig_white

    @render.ui
    def output_graph4ii():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        details = details_df[details_df["TournamentId"] == tournament_id]
        player_name = input.player()
        _, fig_black = player_color_advantage(player_name, details)
        return fig_black
    
    @render.ui
    def output_graph5():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        moves = moves_df[moves_df["TournamentId"] == tournament_id]
        selected_round = input.selected_game()

        # Asegura que sea str por si acaso
        selected_round = str(selected_round).strip()

        if selected_round not in moves["Round"].astype(str).values:
            return "No se encontró la ronda para esta partida."

        fig = engine_evaluation(selected_round, moves)
        return fig

    @render.ui
    def output_graph6():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        moves = moves_df[moves_df["TournamentId"] == tournament_id]
        selected_round = str(input.selected_game()).strip()

        if selected_round not in moves["Round"].astype(str).values:
            return "No se encontró la ronda para esta partida."

        fig = plot_player_times(selected_round, moves)
        return fig


    
    @render.ui
    def output_graph7():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        moves = moves_df[moves_df["TournamentId"] == tournament_id]
        selected_round = str(input.selected_game()).strip()

        if selected_round not in moves["Round"].astype(str).values:
            return "No se encontró la ronda para esta partida."

        fig = time_vs_eval_change_single_game(moves, selected_round)
        return fig
    

    @render.ui
    def output_graph8():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        details = details_df[details_df["TournamentId"] == tournament_id]     
        fig = elo_vs_result(details)
        return fig


    @render.ui
    def output_graph9():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        details = details_df[details_df["TournamentId"] == tournament_id]   
        moves = moves_df[moves_df["TournamentId"] == tournament_id]
        fig = evaluation_distribution_plotly(details, moves)
        return fig

    
    @render.ui
    def heatmap_white():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        moves = moves_df[moves_df["TournamentId"] == tournament_id]
        selected_round = str(input.selected_game()).strip()

        if selected_round not in moves["Round"].astype(str).values:
            return "No se encontró la ronda para esta partida."

        return create_chess_heatmap_plotly(moves, selected_round, "White")


    @render.ui
    def heatmap_black():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]
        moves = moves_df[moves_df["TournamentId"] == tournament_id]
        selected_round = str(input.selected_game()).strip()

        if selected_round not in moves["Round"].astype(str).values:
            return "No se encontró la ronda para esta partida."

        return create_chess_heatmap_plotly(moves, selected_round, "Black")


    @output
    @render.text
    def black_player_result():
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]

        details_df["Round"] = details_df["Round"].astype(str).str.strip()
        selected_round = str(input.selected_game()).strip()
        game_details = details_df[
            (details_df["Round"].astype(str).str.strip() == selected_round) &
            (details_df["TournamentId"] == tournament_id)
        ]

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
        tournament_id = tournaments_df[tournaments_df["Name"] == input.selected_tournament()]["_id"].values[0]

        selected_round = str(input.selected_game()).strip()
        game_details = details_df[
            (details_df["Round"].astype(str).str.strip() == selected_round) &
            (details_df["TournamentId"] == tournament_id)
        ]

        if game_details.empty:
            return "No disponible"
        
        result = game_details["Result"].values[0]
        result = result.split("-")[0]

        if result not in ['1', '0']:
            result = '½'
        
        return ui.HTML(f'<span style="font-size: 20px; font-weight: bold; color: black;">{result}</span>')
    
    @render.ui
    def dropdown_partidas():
        selected_name = input.selected_tournament()
        if selected_name is None or selected_name not in tournaments_df["Name"].values:
            return ui.input_select("selected_game", "Selecciona una partida:", {})

        tournament_id = tournaments_df[tournaments_df["Name"] == selected_name]["_id"].values[0]
        partidas = details_df[details_df["TournamentId"] == tournament_id]

        return ui.input_select(
            "selected_game",
            "Selecciona una partida:",
            {
                str(row["Round"]).strip(): f'{row["Round"]} - {row["White_Player"]} vs {row["Black_Player"]}'
                for _, row in partidas.iterrows()
            }
        )
    
    @render.ui
    def player_dropdown():
        selected_tournament = input.selected_tournament()
        if selected_tournament not in tournaments_df["Name"].values:
            return ui.input_select("player", "Selecciona un jugador:", {})

        tournament_id = tournaments_df[tournaments_df["Name"] == selected_tournament]["_id"].values[0]
        filtered_players = players_df[players_df["TournamentId"] == tournament_id]

        return ui.input_select(
            "player",
            "Selecciona un jugador:",
            {name: name for name in filtered_players["Name"].dropna().unique()}
        )


app = App(app_ui, server)

if __name__ == "__main__":
    app.run()