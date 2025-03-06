import chess.pgn
import csv
import re

def extract_eval_and_time(comment):
    eval_pattern = r'\[%eval\s*(-?[\d.]+)\]'
    time_pattern = r'\[%clk\s*([\d:]+)\]'
    
    eval_match = re.search(eval_pattern, comment)
    time_match = re.search(time_pattern, comment)

    evaluation = eval_match.group(1) if eval_match else ""
    time = time_match.group(1) if time_match else ""

    return evaluation, time

def convertir_tiempo_a_segundos(tiempo):
    if tiempo:
        parts = list(map(int, tiempo.split(':')))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
    return 0

def pgn_to_csv(pgn_file, csv_file):
    with open(pgn_file) as f, open(csv_file, mode="w", newline="") as csvfile:
        fieldnames = ["Event", "Round", "White", "Black", "Result", "WhiteElo", "WhiteTitle", "WhiteFideId", 
                      "BlackElo", "BlackTitle", "BlackFideId", "Variant", "ECO", "Opening", 
                      "Move Number", "Move", "Color", "Evaluation", "Time", "Time (seconds)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break

            headers = game.headers
            board = game.board()

            white_move_number = 1
            black_move_number = 1

            for i, move in enumerate(game.mainline()):
                move_obj = move.move
                evaluation, time = extract_eval_and_time(move.comment)
                time_seconds = convertir_tiempo_a_segundos(time)

                if i % 2 == 0:
                    color = "White"
                    move_number = white_move_number
                    white_move_number += 1
                else:
                    color = "Black"
                    move_number = black_move_number
                    black_move_number += 1

                row = {
                    "Event": headers.get("Event", ""),
                    "Round": headers.get("Round", ""),
                    "White": headers.get("White", ""),
                    "Black": headers.get("Black", ""),
                    "Result": headers.get("Result", ""),
                    "WhiteElo": headers.get("WhiteElo", ""),
                    "WhiteTitle": headers.get("WhiteTitle", ""),
                    "WhiteFideId": headers.get("WhiteFideId", ""),
                    "BlackElo": headers.get("BlackElo", ""),
                    "BlackTitle": headers.get("BlackTitle", ""),
                    "BlackFideId": headers.get("BlackFideId", ""),
                    "Variant": headers.get("Variant", ""),
                    "ECO": headers.get("ECO", ""),
                    "Opening": headers.get("Opening", ""),
                    "Move Number": move_number,
                    "Move": board.san(move_obj),
                    "Color": color,
                    "Evaluation": evaluation,
                    "Time": time,
                    "Time (seconds)": time_seconds
                }

                writer.writerow(row)

                board.push(move_obj)

    print(f"Archivo CSV '{csv_file}' generado correctamente.")

pgn_file = "data/games.pgn"
csv_file = "data/games.csv"
pgn_to_csv(pgn_file, csv_file)
