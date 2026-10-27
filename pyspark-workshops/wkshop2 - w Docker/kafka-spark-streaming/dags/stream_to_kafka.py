import json
import logging
import time

import requests
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s:%(funcName)s:%(levelname)s:%(message)s")
logger = logging.getLogger("stream_to_kafka")

BOOTSTRAP_SERVERS = ["kafka1:19092", "kafka2:19093", "kafka3:19094"]
TOPIC = "random_names"
API_URL = "https://randomuser.me/api/?results=1"


def create_response_dict(url: str = API_URL) -> dict:
    """Appelle l'API Random User et renvoie le premier résultat."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()["results"][0]


def create_final_json(results: dict) -> dict:
    """Ne garde que les champs utiles pour Kafka / Cassandra."""
    return {
        "full_name": f"{results['name']['title']}. {results['name']['first']} {results['name']['last']}",
        "gender": results["gender"],
        "location": f"{results['location']['street']['number']}, {results['location']['street']['name']}",
        "city": results["location"]["city"],
        "country": results["location"]["country"],
        "postcode": str(results["location"]["postcode"]),  # texte : codes alphanumériques possibles
        "latitude": float(results["location"]["coordinates"]["latitude"]),
        "longitude": float(results["location"]["coordinates"]["longitude"]),
        "email": results["email"],
    }


def create_kafka_producer() -> KafkaProducer:
    return KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)


def start_streaming(duration_s: int = 120, interval_s: int = 10) -> None:
    """Envoie un nouvel utilisateur aléatoire toutes les `interval_s` secondes pendant `duration_s` secondes."""
    producer = create_kafka_producer()
    end_time = time.time() + duration_s
    sent = 0
    while time.time() < end_time:
        try:
            kafka_data = create_final_json(create_response_dict())
            producer.send(TOPIC, json.dumps(kafka_data).encode("utf-8"))
            sent += 1
            logger.info("Message %s envoyé : %s", sent, kafka_data["full_name"])
        except Exception as e:  # une erreur API ne doit pas tuer la boucle
            logger.warning("Échec d'un envoi : %s", e)
        time.sleep(interval_s)
    producer.flush()
    producer.close()
    logger.info("Streaming terminé, %s messages envoyés", sent)


if __name__ == "__main__":
    start_streaming()
