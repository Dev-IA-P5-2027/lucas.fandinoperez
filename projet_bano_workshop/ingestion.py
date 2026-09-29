import csv
import os
from pathlib import Path
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

# 1. On charge les variables d'environnement depuis le fichier .env
load_dotenv()


# 2. On se co à ES

es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", os.environ["ES_PASSWORD"])
)

# 3. Variables globales

DEPARTEMENT = "25"
INDEX = f"bano-{DEPARTEMENT}"
CSV_FILE = Path(__file__).parent / "bano-data" / f"bano-{DEPARTEMENT}.csv"
FIELDNAMES = ["id", "numero", "rue", "cp", "commune", "source", "lat", "lon"]

def generer_docs():
    with open(CSV_FILE, mode="r", encoding="utf-8", newline="") as f:
        yield from lire_fichier(f)


def lire_fichier(f):
    reader = csv.DictReader(f, fieldnames=FIELDNAMES)

    for row in reader:
        
        try:
            lat = float(row["lat"])
            lon = float(row["lon"])
            location = {"lat": lat, "lon": lon}
        except (ValueError, KeyError):
            location = None
            
        # JSON
        
        doc = {
            "_index": INDEX,
            "_id": row.get("id"),
            "_source": {
                "id": row.get("id"),
                "numero": row.get("numero"),
                "rue": row.get("rue"),
                "cp": row.get("cp"),
                "commune": row.get("commune"),
                "source": row.get("source"),
                "location": location
            }}
        yield doc
        
def main() -> None:
    if not es.indices.exists(index=INDEX):
        es.indices.create(
            index=INDEX,
            mappings={"properties": {"location": {"type": "geo_point"}}},
            settings={"refresh_interval": "-1", "number_of_replicas": 0},
        )
    else:
        es.indices.put_settings(index=INDEX, settings={"refresh_interval": "-1", "number_of_replicas": 0})

    print("Début de l'ingestion...")
    success = failed = 0
    try:
        for ok, _ in parallel_bulk(es, generer_docs(), thread_count=4, chunk_size=5000, raise_on_error=False):
            if ok:
                success += 1
            else:
                failed += 1
    finally:
        es.indices.put_settings(index=INDEX, settings={"refresh_interval": "1s", "number_of_replicas": 1})
        es.indices.refresh(index=INDEX)
    print(f"Ingestion terminée ! Succès : {success}, Échecs : {failed}")


if __name__ == "__main__":
    main()
