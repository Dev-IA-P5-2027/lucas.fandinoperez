import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

# On se connecte à l'instance ElasticSearch locale

es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", os.environ["ES_PASSWORD"]),
)

# On nomme notre index: bano-25

index_name = "bano-25"

# On définit notre mapping

mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "numero": {"type": "keyword"},
            "rue": {"type": "text"},
            "cp": {"type": "keyword"},
            "commune": {
                "type": "text",
                "fields": {
                    "raw": {"type": "keyword"}
                }
            },
            "source": {"type": "keyword"},
            "location": {"type": "geo_point"}
        }
    }
}

# Suppression si l'index existe déjà (optionnel, pour réinitialiser)
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

# Création de l'index avec le mapping
response = es.indices.create(index=index_name, body=mapping)
print("Index créé :", response)