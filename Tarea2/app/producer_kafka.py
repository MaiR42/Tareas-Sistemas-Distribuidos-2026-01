# Kafka producer
from kafka import KafkaProducer
import json

# Config del producer
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


# Testeo
mensaje = {
    "test": "hola kafka"
}

producer.send(
    "consultas",
    mensaje
)

producer.flush()

print("Mensaje enviado")