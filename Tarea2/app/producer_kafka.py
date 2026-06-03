# Kafka producer
from kafka import KafkaProducer
import json

from config import PROD_QUERY_QUANTITY
from traffic_gen import *

# Config del producer
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

for i in range(PROD_QUERY_QUANTITY):
    consulta = generate_query() # Generar consulta

    print(consulta)
    # Testeo

    producer.send(
        "consultas",
        consulta
    )

    producer.flush()

    print("Mensaje enviado")