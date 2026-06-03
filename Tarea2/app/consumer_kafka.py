# Kafka consumer
import json
import random
import socket
import os
import time


from queries import *
from config import FAILURE_RATE, MAX_RETRIES, TTL, DEBUG

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
print("PID:", os.getpid()) # Ver que se generen consumers diferentes
print("Esperando mensajes...")


for msg in consumer:
    consulta = msg.value
    is_retry = msg.topic == "consultas_retry"
    print(f"TOPIC: {msg.topic} | is_retry: {is_retry} | retries: {consulta['retries']}")

    queue_delay = (time.time() - consulta["created_at"]) # Para las metricas
    r.rpush("metrics:queue_delay", queue_delay)

    
    if consulta["tipo"] == "Q4":
        cache_key = f"query:{consulta['tipo']}:{consulta['zona']}:{consulta['zona_b']}:{consulta['confidence_min']}" # Indicar zona_b
    elif consulta["tipo"] == "Q5":
        cache_key = f"query:{consulta['tipo']}:{consulta['zona']}:{consulta['bins']}" # Indicar bins
    else:
        cache_key = f"query:{consulta['tipo']}:{consulta['zona']}:{consulta['confidence_min']}" # Default para Q1, Q2, Q3

    if is_retry and consulta["retries"] > 0:
        r.incr("metrics:recoveries")
        print("RECOVERY")
        start = r.get(f"failure_start:{consulta['id']}")
        if start:
            recovery_time = time.time() - float(start)
            r.rpush("metrics:recovery_times", recovery_time)
            r.delete(f"failure_start:{consulta['id']}")

    cached = r.get(cache_key)
    if cached and not is_retry:
        r.incr("metrics:hits")
        print("HIT")

         
        r.rpush(
            "metrics:timestamps", # Metricas para throughput
            time.time()
        )
        continue

    else:
        r.incr("metrics:misses")
        if not is_retry:
            print("MISS")
        
        #resultado = procesar_consulta(consulta)
     
        try: # Simular falla
            if random.random() < FAILURE_RATE:
                r.incr("metrics:failures") # Para las metricas

                r.set( # Para recovery time
                    f"failure_start:{consulta['id']}",
                    time.time()
                ) 

                raise Exception("Falla simulada")

            if consulta['retries'] > 0: # Indica que consulta se recupero despues de fallar
                r.incr("metrics:recoveries") # Para las metricas

                start = r.get( # Para recovery time
                    f"failure_start:{consulta['id']}"
                )
                if start:
                    recovery_time = (
                        time.time()
                        - float(start)
                    )
                    r.rpush(
                        "metrics:recovery_times",
                        recovery_time
                    )
                    r.delete(
                        f"failure_start:{consulta['id']}"
                    ) 

            resultado = procesar_consulta(consulta)
        
            r.rpush(
                "metrics:timestamps", # Metricas para throughput
                time.time()
            )

            r.set(cache_key, json.dumps(resultado), ex=TTL)

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
                print("DLQ")
                r.incr("metrics:dlq_count") # Para las metricas
                producer.send(
                    "consultas_dlq",
                    consulta
                )

                print(f"Limite de retrys alcanzado\n DLQ consulta:{consulta['id']}")
            continue

    ##

    print("RECIBIDO:") if DEBUG else 0
    print(consulta) if DEBUG else 0
    print(resultado) if DEBUG else 0