import chess.pgn
import csv
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

def pgn_to_csv(pgn_file, moves_file, details_file, players_file, openings_file):
    players_set = set()
    openings_set = set()
    
    with open(pgn_file) as f, \
         open(moves_file, mode="w", newline="") as moves_csv, \
         open(details_file, mode="w", newline="") as details_csv, \
         open(players_file, mode="w", newline="") as players_csv, \
         open(openings_file, mode="w", newline="") as openings_csv:

        moves_writer = csv.DictWriter(moves_csv, fieldnames=["Round", "Move Number", "Move", "Color", "Evaluation", "Time", "Time (seconds)"])
        details_writer = csv.DictWriter(details_csv, fieldnames=["Round", "Event", "White", "Black", "ECO", "Result"])
        players_writer = csv.DictWriter(players_csv, fieldnames=["Name", "FideId", "Elo"])
        openings_writer = csv.DictWriter(openings_csv, fieldnames=["ECO", "Name"])
        
        moves_writer.writeheader()
        details_writer.writeheader()
        players_writer.writeheader()
        openings_writer.writeheader()

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

            if (white_name, white_fide_id, white_elo) not in players_set:
                players_set.add((white_name, white_fide_id, white_elo))
                players_writer.writerow({"Name": white_name, "FideId": white_fide_id, "Elo": white_elo})

            if (black_name, black_fide_id, black_elo) not in players_set:
                players_set.add((black_name, black_fide_id, black_elo))
                players_writer.writerow({"Name": black_name, "FideId": black_fide_id, "Elo": black_elo})

            if (eco, opening_name) not in openings_set:
                openings_set.add((eco, opening_name))
                openings_writer.writerow({"ECO": eco, "Name": opening_name})

            details_writer.writerow({
                "Round": round_pk,
                "Event": headers.get("Event", ""),
                "White": white_fide_id,
                "Black": black_fide_id,
                "ECO": eco,
                "Result": headers.get("Result", "") 
            })

            move_number = 1
            for i, move in enumerate(game.mainline()):
                move_obj = move.move
                evaluation, time = extract_eval_and_time(move.comment)
                time_seconds = convert_time_to_seconds(time)
                color = "White" if i % 2 == 0 else "Black"

                moves_writer.writerow({
                    "Round": round_pk,
                    "Move Number": move_number,
                    "Move": board.san(move_obj),
                    "Color": color,
                    "Evaluation": evaluation,
                    "Time": time,
                    "Time (seconds)": time_seconds
                })

                if color == "Black":
                    move_number += 1

                board.push(move_obj)

    print(f"Archivos CSV generados correctamente:")
    print(f"  - {moves_file}")
    print(f"  - {details_file}")
    print(f"  - {players_file}")
    print(f"  - {openings_file}")

pgn_file = "data/games.pgn"
moves_file = "data/moves.csv"
details_file = "data/details.csv"
players_file = "data/players.csv"
openings_file = "data/openings.csv"

pgn_to_csv(pgn_file, moves_file, details_file, players_file, openings_file)
