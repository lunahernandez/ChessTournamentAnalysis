from shiny import App, render, req, ui
from pymongo import MongoClient
from pathlib import Path
import faicons as fa
import pandas as pd
import shiny.reactive as reactive
from utils.plots import (players_performance_comparison, players_wins_comparison, 
                         opening_effect, player_color_advantage, get_player_info, 
                         engine_evaluation, plot_player_times, time_vs_eval_change_single_game,
                         elo_vs_result, evaluation_distribution_plotly, create_chess_heatmap_plotly)

from pymongo.errors import ServerSelectionTimeoutError
from utils.pgn_to_mongo import insert_pgn_to_mongo

try:
    client = MongoClient("mongodb://admin:password@mongodb:27017/")
    client.server_info()
    db = client["ChessTournamentAnalysis"]
    print("Conexión a MongoDB exitosa.")
    
except ServerSelectionTimeoutError as e:
    print("No se pudo conectar a MongoDB. Verifica que el contenedor esté corriendo y que la URI sea correcta.")
    print(f"Error: {e}")
    exit(1)


def load_data_by_tournament(tournament_id):
    """Carga los datos de un torneo específico."""

    details_raw = list(db["Details"].find({"TournamentId": tournament_id}))
    if not details_raw:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    details_df = pd.DataFrame(details_raw)

    fide_ids = pd.unique(details_df[["White", "Black"]].values.ravel())

    players_df = pd.DataFrame(list(db["Players"].find({"FideId": {"$in": list(fide_ids)}})))
    if players_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    players_df = players_df.drop_duplicates(subset=["FideId"])

    details_df = details_df.merge(players_df[['FideId', 'Name', 'Elo']], left_on="White", right_on="FideId")
    details_df = details_df.rename(columns={"Name": "White_Player", "Elo": "White_Elo", "White": "White_Fide_ID"}).drop(columns=["FideId"])

    details_df = details_df.merge(players_df[['FideId', 'Name', 'Elo']], left_on="Black", right_on="FideId")
    details_df = details_df.rename(columns={"Name": "Black_Player", "Elo": "Black_Elo", "Black": "Black_Fide_ID"}).drop(columns=["FideId"])

    moves_df = pd.DataFrame(list(db["Moves"].find({"TournamentId": tournament_id})))
    if not moves_df.empty:
        moves_df = moves_df.merge(details_df[['TournamentId', 'Round', 'Event']], on=['Round', 'TournamentId'], how='left')

    return details_df, players_df, moves_df


app_dir = Path(__file__).parent


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.output_ui("tournament_dropdown"),
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
                        ui.output_ui("player_performance_comparison"), full_screen=True
                    ),
                    ui.card(
                        ui.card_header("Comparación de Victorias por Jugador"), 
                        ui.output_ui("player_wins_comparison"), full_screen=True
                    ),
                    col_widths=[6, 6]
                ),
                ui.card(
                        ui.card_header("Comparación de Resultados por Aperturas Más Jugadas"),
                        ui.output_ui("openings_comparison"), full_screen=True
                    ),
                    
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Comparación de Resultados por Jugador según el ELO"), 
                        ui.output_ui("players_comparison_by_elo"), full_screen=True
                    ),
                    ui.card(
                        ui.card_header("Distribución de Evaluaciones por Jugador"), 
                        ui.output_ui("evaluations_distribution"), full_screen=True
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
                            ui.output_ui("white_performance"), full_screen=True
                        ),
                        ui.card(
                            ui.card_header("Rendimiento con negras"),
                            ui.output_ui("black_performance"), full_screen=True
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
                                    ui.column(2, 
                                        [ui.output_ui("white_player_result")
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
                        ui.output_ui("evaluation_per_move"), full_screen=True
                    ),
                    ui.card(
                        ui.card_header("Tiempo Restante por Jugada"),
                        ui.output_ui("time_per_move"), full_screen=True
                    ),
                    ui.card(
                        ui.card_header("Relación entre Tiempo Consumido y Cambio en Evaluación"),
                        ui.output_ui("relation_between_time_evaluation"), full_screen=True
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
            ),
            ui.nav_panel("Importar PGN",
                ui.card(
                    ui.card_header("Importar Torneo desde PGN"),
                    ui.input_file("pgn_file", "Selecciona un archivo PGN (debe tener datos de tiempo)", accept=[".pgn"]),
                    ui.input_text("tournament_name", "Nombre del torneo"),
                    ui.output_text("name_validation"),
                    ui.input_numeric("engine_depth", "Profundidad del motor", value=12, min=1, max=50),
                    ui.input_action_button("import_button", "Importar Torneo"),
                    ui.output_text("import_status")
                )
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


    @reactive.Calc
    def tournament_data():
        selected = input.selected_tournament()
        if not selected:
            # Retornar dataframes vacíos para que los render.ui funcionen
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        tournaments_df = pd.DataFrame(list(db["Tournaments"].find()))
        if tournaments_df.empty or selected not in tournaments_df["Name"].values:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        tournament_id = tournaments_df[tournaments_df["Name"] == selected]["_id"].values[0]
        return load_data_by_tournament(tournament_id)


    @render.ui
    def player_name_card():
        return ui.card(
            ui.card_header(ui.HTML(f"{fa.icon_svg('user', 'solid')} Nombre")),
            ui.card_body(ui.p(input.player()))
        )

    @render.ui
    def player_elo_card():
        details_df, _, _ = tournament_data()
        req(input.player())

        if details_df.empty:
            return ui.card(ui.card_body("No hay datos disponibles para este torneo."))

        player_elo, _ = get_player_info(input.player(), details_df)

        return ui.card(
            ui.card_header(ui.HTML(f"{fa.icon_svg('chart-line')} ELO")),
            ui.card_body(ui.p(str(player_elo)))
        )
    

    @render.ui
    def player_fide_id_card():
        details_df, _, _ = tournament_data()
        req(input.player())

        if details_df.empty:
            return ui.card(ui.card_body("No hay datos disponibles para este torneo."))

        _, fide_id = get_player_info(input.player(), details_df)

        return ui.card(
            ui.card_header(ui.HTML(f"{fa.icon_svg('id-card')} FIDE ID")),
            ui.card_body(ui.p(str(fide_id)))
        )

    @output
    @render.text
    def white_player_info():
        details_df, _, _ = tournament_data()
        req(input.selected_game())

        if details_df.empty:
            return "No disponible"

        selected_round = str(input.selected_game()).strip()

        game_details = details_df[
            details_df["Round"].astype(str).str.strip() == selected_round
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
        details_df, _, _ = tournament_data()
        req(input.selected_game())

        if details_df.empty:
            return "No disponible"

        selected_round = str(input.selected_game()).strip()

        game_details = details_df[
            details_df["Round"].astype(str).str.strip() == selected_round
        ]

        if game_details.empty:
            return "No disponible"

        player_name = game_details["Black_Player"].values[0]
        elo = game_details["Black_Elo"].values[0]
        fide_id = game_details["Black_Fide_ID"].values[0]

        return ui.HTML(f"Nombre: {player_name}<br>ELO: {elo}<br>FIDE ID: {fide_id}")
    
    @render.ui
    def player_performance_comparison():
        details_df, _, _ = tournament_data()
        if details_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        graph_html = players_performance_comparison(details_df)
        return ui.HTML(graph_html)

    @render.ui
    def player_wins_comparison():
        details_df, _, _ = tournament_data()
        if details_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        graph_html = players_wins_comparison(details_df)
        return ui.HTML(graph_html)

    @render.ui
    def openings_comparison():
        details_df, _, _ = tournament_data()
        if details_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        return opening_effect(details_df)

    @render.ui
    def white_performance():
        details_df, _, _ = tournament_data()
        if details_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        fig_white, _ = player_color_advantage(input.player(), details_df)
        if fig_white is None:
            return ui.HTML("No hay datos disponibles con este color.")
        else:
            return fig_white

    @render.ui
    def black_performance():
        details_df, _, _ = tournament_data()
        if details_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        _, fig_black = player_color_advantage(input.player(), details_df)
        if fig_black is None:
            return ui.HTML("No hay datos disponibles con este color.")
        else:
            return fig_black

    @render.ui
    def evaluation_per_move():
        _, _, moves_df = tournament_data()
        if moves_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        selected_round = str(input.selected_game()).strip()

        if selected_round not in moves_df["Round"].astype(str).values:
            return "No se encontró la ronda para esta partida."

        return engine_evaluation(selected_round, moves_df)

    @render.ui
    def time_per_move():
        _, _, moves_df = tournament_data()
        if moves_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        selected_round = str(input.selected_game()).strip()

        if selected_round not in moves_df["Round"].astype(str).values:
            return "No se encontró la ronda para esta partida."

        return plot_player_times(selected_round, moves_df)

    @render.ui
    def relation_between_time_evaluation():
        _, _, moves_df = tournament_data()
        if moves_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        selected_round = str(input.selected_game()).strip()

        if selected_round not in moves_df["Round"].astype(str).values:
            return "No se encontró la ronda para esta partida."

        return time_vs_eval_change_single_game(moves_df, selected_round)

        
    @render.ui
    def players_comparison_by_elo():
        details_df, _, _ = tournament_data()
        if details_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        return elo_vs_result(details_df)


    @render.ui
    def evaluations_distribution():
        details_df, _, moves_df = tournament_data()
        if details_df.empty or moves_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        return evaluation_distribution_plotly(details_df, moves_df)


    @render.ui
    def heatmap_white():
        _, _, moves_df = tournament_data()
        if moves_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        selected_round = str(input.selected_game()).strip()

        if selected_round not in moves_df["Round"].astype(str).values:
            return "No se encontró la ronda para esta partida."

        return create_chess_heatmap_plotly(moves_df, selected_round, "White")


    @render.ui
    def heatmap_black():
        _, _, moves_df = tournament_data()
        if moves_df.empty:
            return ui.HTML("<b>No hay datos disponibles para este torneo.</b>")

        selected_round = str(input.selected_game()).strip()

        if selected_round not in moves_df["Round"].astype(str).values:
            return "No se encontró la ronda para esta partida."

        return create_chess_heatmap_plotly(moves_df, selected_round, "Black")


    @output
    @render.text
    def black_player_result():
        details_df, _, _ = tournament_data()
        if details_df.empty:
            return ""

        selected_round = str(input.selected_game()).strip()

        game_details = details_df[
            (details_df["Round"] == selected_round)
        ]

        if game_details.empty:
            return "No disponible"

        result = game_details["Result"].values[0].split("-")[1]
        if result not in ['1', '0']:
            result = '½'

        return ui.HTML(f'<span style="font-size: 20px; font-weight: bold; color: white;">{result}</span>')

    @output
    @render.text
    def white_player_result():
        details_df, _, _ = tournament_data()
        if details_df.empty:
            return ""

        selected_round = str(input.selected_game()).strip()

        game_details = details_df[
            (details_df["Round"].astype(str).str.strip() == selected_round)
        ]

        if game_details.empty:
            return "No disponible"

        result = game_details["Result"].values[0].split("-")[0]
        if result not in ['1', '0']:
            result = '½'

        return ui.HTML(f'<span style="font-size: 20px; font-weight: bold; color: black;">{result}</span>')
    
    @render.ui
    def dropdown_partidas():
        details_df, _, _ = tournament_data()
        tournaments_df = pd.DataFrame(list(db["Tournaments"].find()))
        
        if tournaments_df.empty:
            return ui.HTML("No hay datos disponibles. Por favor, importa un torneo primero.")
        
        selected_name = input.selected_tournament()
        if selected_name is None or selected_name not in tournaments_df["Name"].values:
            return ui.input_select("selected_game", "Selecciona una partida:", {})
        
        return ui.input_select(
            "selected_game",
            "Selecciona una partida:",
            {
                str(row["Round"]).strip(): f'{row["Round"]} - {row["White_Player"]} vs {row["Black_Player"]}'
                for _, row in details_df.iterrows()
            }
        )

    @render.ui
    def player_dropdown():
        details_df, _, _ = tournament_data()
        tournaments_df = pd.DataFrame(list(db["Tournaments"].find()))
        
        if tournaments_df.empty:
            return ui.HTML("No hay datos disponibles. Por favor, importa un torneo primero.")
        
        selected_tournament = input.selected_tournament()
        if selected_tournament not in tournaments_df["Name"].values:
            return ui.input_selectize("player", "Selecciona un jugador:", choices={})

        players_in_tournament = pd.concat([ 
            details_df["White_Player"], details_df["Black_Player"]
        ]).dropna().unique()

        return ui.input_selectize(
            "player",
            "Selecciona un jugador:",
            choices={name: name for name in sorted(players_in_tournament)},
            options={"placeholder": "Escribe para filtrar..."}
        )


    @render.ui
    def tournament_dropdown():
        tournaments = pd.DataFrame(list(db["Tournaments"].find()))
        return ui.input_select(
            "selected_tournament", "Selecciona un torneo:",
            choices={row["Name"]: row["Name"] for _, row in tournaments.iterrows()}
        )


    @render.ui
    def tournament_dropdown():
        tournaments = pd.DataFrame(list(db["Tournaments"].find()))
        return ui.input_select(
            "selected_tournament", "Selecciona un torneo:",
            choices={row["Name"]: row["Name"] for _, row in tournaments.iterrows()}
        )


    @output
    @render.text
    def name_validation():
        tournaments_df = pd.DataFrame(list(db["Tournaments"].find()))
        name = input.tournament_name()
        
        if not name:
            return ""
        
        if tournaments_df.empty:
            return "✅ Nombre válido."

        if name in tournaments_df["Name"].values:
            return "❌ Nombre de torneo ya existente. Si desea importar igualmente, tenga en cuenta que habrá duplicados."
        
        return "✅ Nombre válido."

    
    status_text = reactive.Value("")

    @output
    @render.text
    def import_status():
        if input.import_button() == 0:
            return ""

        pgn_file_info = input.pgn_file()
        tournament_name = input.tournament_name()
        engine_path = "/app/evaluator/stockfish/stockfish"
        engine_depth = input.engine_depth()

        if not pgn_file_info or not tournament_name or not engine_path or not engine_depth:
            return "⚠️ Por favor completa todos los campos."

        file_path = pgn_file_info[0]["datapath"]
        status_text.set("⌛ Importando torneo...")

        try:
            insert_pgn_to_mongo(
                pgn_file=file_path,
                tournament_name=tournament_name,
                engine_path=engine_path,
                engine_depth=engine_depth
            )
            status_text.set("✅ Torneo importado correctamente. Por favor, actualiza la página.")
        except Exception as e:
            status_text.set(f"❌ Error durante la importación: {e}")

        return status_text.get()


app = App(app_ui, server)

if __name__ == "__main__":
    app.run()