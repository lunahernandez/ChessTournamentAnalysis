from pymongo import MongoClient

def create_collections():
    client = MongoClient("mongodb://admin:password@mongodb:27017/")
    db = client["ChessTournamentAnalysis"]

    collections = ["Moves", "Details", "Players", "Openings", "Tournaments"]
    for col in collections:
        if col not in db.list_collection_names():
            db.create_collection(col)
            print(f"Colección '{col}' creada.")
        else:
            print(f"Colección '{col}' ya existe.")

if __name__ == "__main__":
    create_collections()
