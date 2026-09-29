import os
from typing import Any

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

# 1. On charge le .env et on se co à ES (comme dans ingestion.py)
load_dotenv()

es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", os.environ["ES_PASSWORD"])
)

INDEX = "bano-25"

# Point de test : une adresse prise au hasard dans bano-25.csv (Besançon)
POINT = {"lat": 47.245912, "lon": 6.034779}


def afficher(titre: str, resp: Any) -> None:
    print(f"\n=== {titre} ===")
    print(f"Total : {resp['hits']['total']['value']} | took : {resp['took']} ms")
    for hit in resp["hits"]["hits"]:
        s = hit["_source"]
        extra = f" | distance : {hit['sort'][0]:.0f} m" if "sort" in hit else ""
        score = f"{hit['_score']} " if hit["_score"] is not None else ""
        print(f"{score}-> {s['numero']} {s['rue']}, {s['cp']} {s['commune']}{extra}")


# 2. Première requête : recherche d'adresse avec 3 match dans un should
# Le score = somme des clauses qui matchent (BM25), donc plus y'a de champs
# qui collent, plus le doc remonte.
# dfs_query_then_fetch pour avoir des scores cohérents entre les shards.
# Attention : "besancon" sans cédille ne matche pas (analyzer standard qui
# garde les accents), d'où le "besançon" ici. Piste pour la partie 8 :
# asciifolding sur rue / commune.
def recherche_adresse() -> None:
    resp = es.search(
        index=INDEX,
        search_type="dfs_query_then_fetch",
        size=1,
        query={
            "bool": {
                "should": [
                    {"match": {"numero": "23"}},
                    {"match": {"rue": "rue lanchy"}},
                    {"match": {"commune": "besançon"}},
                ]
            }
        },
    )
    afficher("Recherche d'adresse (should)", resp)


# 3. Recherche géo : toutes les adresses dans un rayon de 200m autour du point
# Le geo_distance est mis dans un filter (pas de calcul de score, et c'est
# mis en cache), puis on trie par distance avec _geo_distance pour avoir
# les plus proches en premier.
def recherche_rayon(distance: str = "200m") -> None:
    resp = es.search(
        index=INDEX,
        size=5,
        query={
            "bool": {
                "filter": {
                    "geo_distance": {"distance": distance, "location": POINT}
                }
            }
        },
        sort=[{"_geo_distance": {"location": POINT, "order": "asc", "unit": "m"}}],
    )
    afficher(f"Adresses dans un rayon de {distance}", resp)


if __name__ == "__main__":
    recherche_adresse()
    recherche_rayon()
