# Kafka consumer
import json
import random
import socket
import os
import time


from queries import *
from config import FAILURE_RATE, MAX_RETRIES

import redis
r = redis.Redis(
    host="cache",
    port=6379,
    decode_responses=True
)


# Config del consumer
from kafka import KafkaConsumer
consumer = KafkaConsumer(
    "consultas",
    "consultas_retry",

    bootstrap_servers="kafka:9092",

    value_deserializer=lambda m:
        json.loads(m.decode("utf-8")),

    auto_offset_reset="earliest",

    group_id="grupo1"
)

from kafka import KafkaProducer
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def procesar_consulta(c):
    if c["tipo"] == "Q1":
        return q1_count(
            c["zona"],
            c["confidence_min"]
        )

    elif c["tipo"] == "Q2":
        return q2_area(
            c["zona"],
            c["confidence_min"]
        )

    elif c["tipo"] == "Q3":
        return q3_density(
            c["zona"],
            c["confidence_min"]
        )

    elif c["tipo"] == "Q4":
        return q4_compare(
            c["zona"],
            c["zona_b"],
            c["confidence_min"]
        )

    elif c["tipo"] == "Q5":
        return q5_confidence_dist(
            c["zona"],
            c["bins"]
        )
    if "tipo" not in c:
        print("Mensaje inválido:", c)
        return None

# Testeo
print("iniciado el consumer:", socket.gethostname())
print("PID:", os.getpid())
print("Esperando mensajes...")



for msg in consumer:
    #print("TOPIC:", msg.topic)
    #print("VALUE:", msg.value)
    consulta = msg.value

    queue_delay = (time.time() - consulta["created_at"]) # Para las metricas
    r.rpush("metrics:queue_delay", queue_delay)

    print(
        "Consumer:",
        socket.gethostname(),
        "Partition:",
        msg.partition
    )

    cache_key = json.dumps(
        consulta,
        sort_keys=True
    )
    cached = r.get(cache_key)
    if cached:
        r.incr("metrics:hits")
        print("HIT")
        continue

    else:
        r.incr("metrics:misses")
        print("MISS")

        resultado = procesar_consulta(
            consulta
        )

        r.set(
            cache_key,
            json.dumps(resultado),
            ex=60
        )

    try: # Simular falla
        if random.random() < FAILURE_RATE:
            r.incr("metrics:failures") # Para las metricas
            raise Exception("Falla simulada")

        if consulta["retries"] > 0: # Indica que consulta se recupero despues de fallar
            r.incr("metrics:recoveries") # Para las metricas

        resultado = procesar_consulta(consulta)

    except Exception: # Hacer retry
        r.incr("metrics:retry_count") # Para las metricas
        consulta["retries"] += 1

        if consulta["retries"] <= MAX_RETRIES: # Si se no se llego al limite entonces realizar retry

            producer.send(
                "consultas_retry",
                consulta
            )

            print(
                f"Retry {consulta['retries']} "
                f"para consulta:{consulta['id']}"
            )

        else: # Sino indicar a DLQ
            r.incr("metrics:dlq_count") # Para las metricas
            producer.send(
                "consultas_dlq",
                consulta
            )

            print(f"Limite de retrys alcanzado\n DLQ consulta:{consulta['id']}")
        continue



    

    ##

    print("RECIBIDO:")
    print(consulta)

    print(resultado)