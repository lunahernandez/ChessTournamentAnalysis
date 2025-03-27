from pymongo import MongoClient

def create_collections():
    client = MongoClient("mongodb://admin:password@localhost:27017/")
    db = client["chess_db"]

    # Crea las colecciones vacías
    collections = ["moves", "details", "players", "openings"]
    for col in collections:
        if col not in db.list_collection_names():
            db.create_collection(col)
            print(f"Colección '{col}' creada.")
        else:
            print(f"⚠️ Colección '{col}' ya existe.")

if __name__ == "__main__":
    create_collections()
