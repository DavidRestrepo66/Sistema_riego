import sys, os, json
from datetime import datetime
sys.path.insert(0, 'SensoresWeb_MongoDB')
from config import Config
from pymongo import MongoClient
from bson import ObjectId


def serialize_doc(doc):
    """Converts ObjectId → str, datetime → ISO string, recursively handles dicts and lists."""
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    else:
        return doc


def export_collection(col, name, output_dir):
    docs = list(col.find())
    serialized = [serialize_doc(doc) for doc in docs]
    output_path = os.path.join(output_dir, f"{name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)
    print(f"  {name}: {len(serialized)} documentos exportados → {output_path}")


if __name__ == "__main__":
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.DATABASE_NAME]
    os.makedirs("mongo_export", exist_ok=True)
    print("Iniciando exportación de colecciones MongoDB...")
    for name in ["usuarios", "lecturas", "configuraciones", "alertas"]:
        export_collection(db[name], name, "mongo_export")
    client.close()
    print("Exportación completada.")
