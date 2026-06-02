# Kafka consumer
from kafka import KafkaConsumer
import json

# Config del consumer
consumer = KafkaConsumer(
    "consultas",

    bootstrap_servers="kafka:9092",

    value_deserializer=lambda m:
        json.loads(m.decode("utf-8")),

    auto_offset_reset="earliest",

    group_id="grupo1"
)

# Testeo
print("Esperando mensajes...")

for msg in consumer:

    print(msg.value)