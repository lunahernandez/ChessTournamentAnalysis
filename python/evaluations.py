import pymongo
import matplotlib.pyplot as plt

def get_game_evaluations(mongo_uri, db_name, collection_name):
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    
    games = collection.find()
    game_data = {}
    
    for game in games:
        game_id = game["Event"]
        if game_id not in game_data:
            game_data[game_id] = {"moves": [], "evaluations": []}
        
        evaluation = float(game["Evaluation"]) if "Evaluation" in game and game["Evaluation"] else 0
        
        game_data[game_id]["evaluations"].append(evaluation)
        game_data[game_id]["moves"].append(game["Move Number"])
    
    client.close()
    return game_data


def plot_evaluations(game_data):
    plt.figure(figsize=(10, 6))
    
    for game_id, data in game_data.items():
        plt.plot(data["moves"], data["evaluations"], marker="o", label=game_id)
    
    plt.axhline(y=0, color='black', linestyle='--', linewidth=1)
    plt.xlabel("Move Number")
    plt.ylabel("Evaluation")
    plt.title("Stockfish Evaluation per Move")
    plt.legend()
    plt.grid()
    plt.show()


MONGO_URI = "mongodb://admin:password@localhost:27017/ChessTournamentAnalysis?authSource=admin"
DB_NAME = "ChessTournamentAnalysis"
COLLECTION_NAME = "CerradoIMBarcelonaJunio2024"

game_data = get_game_evaluations(MONGO_URI, DB_NAME, COLLECTION_NAME)

plot_evaluations(game_data)
