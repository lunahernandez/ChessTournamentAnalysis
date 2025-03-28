from pymongo import MongoClient
import chess.pgn
import re

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

def insert_pgn_to_mongo(pgn_file):
    client = MongoClient("mongodb://localhost:27017/")  # Conexión sin autenticación
    db = client["chess_db"]

    players_set = set()
    openings_set = set()

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
            event = headers.get("Event", "")
            result = headers.get("Result", "")

            # Insertar jugadores si no están
            if (white_name, white_fide_id, white_elo) not in players_set:
                players_set.add((white_name, white_fide_id, white_elo))
                db.players.insert_one({
                    "Name": white_name, 
                    "FideId": white_fide_id, 
                    "Elo": int(white_elo) if white_elo else 0  # Aseguramos que Elo sea un número entero
                })

            if (black_name, black_fide_id, black_elo) not in players_set:
                players_set.add((black_name, black_fide_id, black_elo))
                db.players.insert_one({
                    "Name": black_name, 
                    "FideId": black_fide_id, 
                    "Elo": int(black_elo) if black_elo else 0  # Aseguramos que Elo sea un número entero
                })

            # Insertar apertura si no está
            if (eco, opening_name) not in openings_set:
                openings_set.add((eco, opening_name))
                db.openings.insert_one({"ECO": eco, "Name": opening_name})

            # Insertar detalles de la partida
            db.details.insert_one({
                "Round": round_pk if round_pk else "Unknown",
                "Event": event if event else "Unknown",
                "White": white_fide_id if white_fide_id else "Unknown",
                "Black": black_fide_id if black_fide_id else "Unknown",
                "ECO": eco if eco else "Unknown",
                "Result": result if result else "Unknown"
            })

            # Insertar movimientos
            move_number = 1
            for i, move in enumerate(game.mainline()):
                move_obj = move.move
                evaluation, time = extract_eval_and_time(move.comment)
                time_seconds = convert_time_to_seconds(time)
                color = "White" if i % 2 == 0 else "Black"

                db.moves.insert_one({
                    "Round": round_pk if round_pk else "Unknown",
                    "Move Number": move_number,
                    "Move": board.san(move_obj),
                    "Color": color,
                    "Evaluation": float(evaluation) if evaluation is not None else 0.0,  # Aseguramos que Evaluation sea float
                    "Time": time if time else "Unknown",
                    "Time (seconds)": int(time_seconds) if time_seconds else 0  # Aseguramos que Time (seconds) sea entero
                })

                if color == "Black":
                    move_number += 1

                board.push(move_obj)

    print("✅ PGN importado correctamente a MongoDB.")

if __name__ == "__main__":
    insert_pgn_to_mongo("../data/games.pgn")
