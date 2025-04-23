import argparse
from pymongo import MongoClient
import chess.pgn
import re
import chess.engine

STOCKFISH_PATH = "C:/Program Files/ChessBase/stockfish/stockfish-windows-x86-64-avx2"
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

def extract_eval_and_time(comment):
    eval_pattern = r'\[%eval\s*(-?[\d.]+)\]'
    time_pattern = r'\[%clk\s*([\d:]+)\]'
    
    eval_match = re.search(eval_pattern, comment)
    time_match = re.search(time_pattern, comment)

    evaluation = float(eval_match.group(1)) if eval_match else None
    time = time_match.group(1) if time_match else ""

    return evaluation, time

def convert_time_to_seconds(time):
    if time:
        parts = list(map(int, time.split(':')))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
    return 0

def insert_pgn_to_mongo(pgn_file, tournament_name):
    client = MongoClient("mongodb://admin:password@host.docker.internal:27017/")
    db = client["ChessTournamentAnalysis"]

    players_set = set()
    openings_set = set()

    tournament = db.Tournaments.find_one({"Name": tournament_name})
    if not tournament:
        tournament_id = db.Tournaments.insert_one({"Name": tournament_name}).inserted_id
    else:
        tournament_id = tournament["_id"]

    with open(pgn_file) as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break

            headers = game.headers
            board = game.board()

            round_pk = headers.get("Round", "")
            white_fide_id = headers.get("WhiteFideId", "")
            black_fide_id = headers.get("BlackFideId", "")
            white_name = headers.get("White", "")
            black_name = headers.get("Black", "")
            white_elo = int(headers.get("WhiteElo", 0)) if headers.get("WhiteElo", "").isdigit() else None
            black_elo = int(headers.get("BlackElo", 0)) if headers.get("BlackElo", "").isdigit() else None
            eco = headers.get("ECO", "")
            opening_name = headers.get("Opening", "")
            result = headers.get("Result", "")

            if (white_name, white_fide_id, white_elo) not in players_set:
                players_set.add((white_name, white_fide_id, white_elo))
                db.Players.insert_one({
                    "Name": white_name, 
                    "FideId": white_fide_id, 
                    "Elo": int(white_elo) if white_elo else 0
                })

            if (black_name, black_fide_id, black_elo) not in players_set:
                players_set.add((black_name, black_fide_id, black_elo))
                db.Players.insert_one({
                    "Name": black_name, 
                    "FideId": black_fide_id, 
                    "Elo": int(black_elo) if black_elo else 0
                })

            # Insertar apertura si no está
            if (eco, opening_name) not in openings_set:
                openings_set.add((eco, opening_name))
                db.Openings.insert_one({"ECO": eco, "Name": opening_name})

            # Insertar detalles de la partida
            details_id = db.Details.insert_one({
                "TournamentId": tournament_id,
                "Round": round_pk if round_pk else "Unknown",
                "Event": tournament_name if tournament_name else "Unknown",
                "White": white_fide_id if white_fide_id else "Unknown",
                "Black": black_fide_id if black_fide_id else "Unknown",
                "ECO": eco if eco else "Unknown",
                "Result": result if result else "Unknown"
            }).inserted_id

            # Insertar movimientos
            move_number = 1
            for i, move in enumerate(game.mainline()):
                move_obj = move.move
                evaluation, time = extract_eval_and_time(move.comment)
                time_seconds = convert_time_to_seconds(time)
                color = "White" if i % 2 == 0 else "Black"

                if evaluation is None:
                    info = engine.analyse(board, chess.engine.Limit(depth=15))
                    score = info["score"].white()

                    if score.is_mate():
                        evaluation = 100 if score.mate() > 0 else -100
                    else:
                        evaluation = score.score() / 100.0

                db.Moves.insert_one({
                    "TournamentId": tournament_id,
                    "GameId": details_id,
                    "Round": round_pk if round_pk else "Unknown",
                    "Move Number": move_number,
                    "Move": board.san(move_obj),
                    "Color": color,
                    "Evaluation": float(evaluation) if evaluation is not None else 0.0,
                    "Time": time if time else "Unknown",
                    "Time (seconds)": int(time_seconds) if time_seconds else 0
                })

                if color == "Black":
                    move_number += 1

                board.push(move_obj)

    print("✅ PGN importado correctamente a MongoDB.")
    engine.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Importar un archivo PGN a MongoDB y calcular evaluaciones de jugadas.")
    parser.add_argument("pgn_file", type=str, help="Ruta al archivo PGN a importar.")
    parser.add_argument("-n", "--tournament", type=str, required=True, help="Nombre del torneo a asociar con las partidas.")
    
    args = parser.parse_args()
    
    insert_pgn_to_mongo(args.pgn_file, args.tournament)
