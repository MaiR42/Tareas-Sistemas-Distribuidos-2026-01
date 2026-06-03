# Solamente para mostrar las metricas
import redis
import numpy as np
import json
from config import *

from kafka import KafkaConsumer, TopicPartition


def get_backlog_size():
    try:
        temp_consumer = KafkaConsumer(
            bootstrap_servers="kafka:9092",
            group_id="grupo1",
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )

        topicos = ["consultas", "consultas_retry"]

        backlog_por_topico = {}
        total_backlog = 0

        for topico in topicos:

            partitions = temp_consumer.partitions_for_topic(topico)

            if not partitions:
                continue

            tps = [
                TopicPartition(topico, p)
                for p in partitions
            ]

            end_offsets = temp_consumer.end_offsets(tps)

            committed = {
                tp: temp_consumer.committed(tp) or 0
                for tp in tps
            }

            backlog_topico = 0

            for tp in tps:

                lag = (
                    end_offsets[tp]
                    - committed[tp]
                )

                backlog_topico += lag

            backlog_por_topico[topico] = backlog_topico
            total_backlog += backlog_topico

        temp_consumer.close()

        return backlog_por_topico, total_backlog

    except Exception as e:
        print("Error midiendo backlog:", e)
        return {}, -1


print("========================================")
print("Backlog Kafka")
print("========================================")
backlogs, backlog_total = get_backlog_size()
print("Backlog consultas:", backlogs.get("consultas", 0))

print("Backlog retry:", backlogs.get("consultas_retry", 0))

print("Backlog total:", backlog_total)


# Metricas Tarea 1
r = redis.Redis(
    host="cache",
    port=6379,
    decode_responses=True
)
info = r.info('stats')
hits = int(r.get("metrics:hits") or 0) # Utilizado
misses = int(r.get("metrics:misses") or 0) # Utilizado
eviction = int(r.get("metrics:evicted_keys") or 0)
total = hits + misses # Utilizado
hit_rate = 0 # Utilizado
if total != 0:
    hit_rate = hits/total
evicted_keys = info.get("evicted_keys", 0)
expired_keys = info.get('expired_keys', 0)
capacity = r.config_get("maxmemory") # Utilizado
mem_info = r.info('memory') # Utilizado
used_memory_bytes = mem_info.get("used_memory", 0)  # Utilizado
retry_count = int(r.get("metrics:retry_count") or 0)
dlq_count = int(r.get("metrics:dlq_count") or 0)

failures = int(r.get("metrics:failures") or 0)
recoveries = int(r.get("metrics:recoveries") or 0)

recovery_rate = 0
if failures > 0:
    recovery_rate = recoveries / failures

lat = [
    float(x)
    for x in r.lrange(
        "metrics:latency",
        0,
        -1
    )
]

p50 = np.percentile(lat, 50) if lat else 0
p95 = np.percentile(lat, 95) if lat else 0

queue_delay = [
    float(x)
    for x in r.lrange(
        "metrics:queue_delay",
        0,
        -1
    )
]
avg_queue_delay = (sum(queue_delay) / len(queue_delay)) if queue_delay else 0

timestamps = [ # Para el throughput
    float(x)
    for x in r.lrange(
        "metrics:timestamps",
        0,
        -1
    )
]
if len(timestamps) > 1:
    total_time = (
        timestamps[-1]
        - timestamps[0]
    )
    throughput = (
        len(timestamps)
        / total_time
    )
else:
    throughput = 0

recovery_times = [
    float(x)
    for x in r.lrange(
        "metrics:recovery_times",
        0,
        -1
    )
]
avg_recovery_time = (sum(recovery_times) / len(recovery_times)) if recovery_times else 0


# Mostrar Metricas
print("========================================")
print("Metricas Generales y del Sistema Cache (Tarea 1)")
print("========================================")

print("Hits:", hits) # Utilizado
print("Misses:", misses) # Utilizado
print("Total de consultas realizadas: ", total) # Utilizado
print(f"Hit rate: {round(hit_rate*100, 4)}%") # Utilizado
#print("Evicted keys: ", evicted_keys)
#print("p50:", p50)
#print("p95:", p95)
#print(f"Capacidad: {int(capacity['maxmemory']) / (1024*1024)} MB") # Utilizado
#print(f"Memoria usada en cache actualmente: {used_memory_bytes / (1024*1024)} MB") # Utilizado
#print("Consultas expiradas (por TTL): ",expired_keys) # Utilizado
#print("Throughput (req/s):", throughput)

print("========================================")
print("Metricas Sistema de Recuperacion (Tarea 2)")
print("========================================")

print("Distribucion de consultas: ", GEN_TRAFIC_DISTR)
print("TTL: ", TTL)
print("FAILURE_RATE (Prob. de fallo): ", FAILURE_RATE*100, "%")
print("Cantidad max. de retries: ", MAX_RETRIES)

print("Retries:", retry_count) # Pedido
print(f"Retry Rate: {round(retry_count/total*100,2)}%") if total!=0 else 0 # Pedido

print("DLQ:", dlq_count) # Pedido
print(f"DLQ Rate: {round(dlq_count/total*100,2)}%") if total!=0 else 0 # Pedido

print("Recoveries:", recoveries)
print(f"Recovery Rate: {round(recovery_rate*100,2)}%") # Pedido
print("Recovery Time: ", avg_recovery_time) # Pedido

print("Queue delay promedio: ", avg_queue_delay) 

print("Throughput (req/s): ", round(throughput, 2)) # Pedido

# Exportar Metricas

import csv
import os
from datetime import datetime

row = [
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    GEN_TRAFIC_DISTR,
    TTL,
    FAILURE_RATE,
    MAX_RETRIES,
    retry_count,
    round(retry_count/total*100,2) if total != 0 else 0,
    dlq_count,
    round(dlq_count/total*100,2) if total != 0 else 0,
    recoveries,
    round(recovery_rate*100,2),
    avg_recovery_time,
    avg_queue_delay,
    round(throughput,2),
    hits,
    misses,
    hit_rate
]

os.makedirs("results", exist_ok=True)

file_path = "results/results.csv"

file_exists = os.path.isfile(file_path)

with open(file_path, "a", newline="") as f:
    writer = csv.writer(f)

    if not file_exists:
        writer.writerow([
            "timestamp",
            "distribution",
            "ttl",
            "failure_rate",
            "max_retries",
            "retries",
            "retry_rate",
            "dlq",
            "dlq_rate",
            "recoveries",
            "recovery_rate",
            "recovery_time",
            "queue_delay",
            "throughput",
            "hits", # añadido
            "misses",
            "hit_rate"
        ])

    writer.writerow(row)