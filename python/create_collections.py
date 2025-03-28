from pymongo import MongoClient

def create_collections():
    client = MongoClient("mongodb://admin:password@mongodb:27017/")  # Conexión con MongoDB
    db = client["ChessTournamentAnalysis"]  # Nombre de la base de datos

    # Crea las colecciones vacías
    collections = ["Moves", "Details", "Players", "Openings"]
    for col in collections:
        if col not in db.list_collection_names():
            db.create_collection(col)
            print(f"Colección '{col}' creada.")
        else:
            print(f"⚠️ Colección '{col}' ya existe.")

        # Insertar un documento vacío para asegurarnos de que la base de datos y la colección se creen si no existen
        db[col].insert_one({})  # Insertamos un documento vacío en la colección

if __name__ == "__main__":
    create_collections()
