# Kafka producer
from kafka import KafkaProducer
import json

from traffic_gen import *

# Config del producer
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

consulta = generate_query() # Generar consulta

print(consulta)
# Testeo

producer.send(
    "consultas",
    consulta
)

producer.flush()

print("Mensaje enviado")