# Solamente para mostrar las metricas

import redis
import numpy as np

from config import *

r = redis.Redis(host="cache", port=6379, decode_responses=True)

# Metricas Tarea 1

info = r.info('stats')

hits = int(r.get("metrics:hits") or 0) # Utilizado
misses = int(r.get("metrics:misses") or 0) # Utilizado
lat = [float(x) for x in r.lrange("metrics:latency", 0, -1)]
eviction = int(r.get("metrics:evicted_keys") or 0)
total = hits + misses # Utilizado
hit_rate = 0 # Utilizado
if total != 0:
    hit_rate = hits/total

p50 = np.percentile(lat, 50) if lat else 0
p95 = np.percentile(lat, 95) if lat else 0

evicted_keys = info.get("evicted_keys", 0)
expired_keys = info.get('expired_keys', 0)

capacity = r.config_get("maxmemory") # Utilizado
mem_info = r.info('memory') # Utilizado
used_memory_bytes = mem_info.get("used_memory", 0)  # Utilizado

timestamps = [float(x) for x in r.lrange("metrics:timestamps", 0, -1)]

if len(timestamps) > 1:
    total_time = timestamps[-1] - timestamps[0]
    throughput = len(timestamps) / total_time
else:
    throughput = 0

# Metricas Tarea 2

retry_count = int(r.get("metrics:retry_count") or 0)
dlq_count = int(r.get("metrics:dlq_count") or 0)

failures = int(r.get("metrics:failures") or 0)
recoveries = int(r.get("metrics:recoveries") or 0)

recovery_rate = 0

if failures > 0:
    recovery_rate = recoveries / failures


# Mostrar Metricas
print("========================================")
print("Metricas Generales y del Sistema Cache (Tarea 1)")
print("========================================")

print("Hits:", hits) # Utilizado
print("Misses:", misses) # Utilizado
print("Total de consultas realizadas: ", total) # Utilizado
print(f"Hit rate: {round(hit_rate*100, 4)}%") # Utilizado
print("Evicted keys: ", evicted_keys)
print("p50:", p50)
print("p95:", p95)
print(f"Capacidad: {int(capacity['maxmemory']) / (1024*1024)} MB") # Utilizado
print(f"Memoria usada en cache actualmente: {used_memory_bytes / (1024*1024)} MB") # Utilizado
print("Consultas expiradas (por TTL): ",expired_keys) # Utilizado
print("Throughput (req/s):", throughput)

print("========================================")
print("Metricas Sistema de Recuperacion (Tarea 2)")
print("========================================")

print("Distribucion de consultas", GEN_TRAFIC_DISTR)
print("TTL: ", TTL)
print("FAILURE_RATE (Prob. de fallo): ", FAILURE_RATE*100, "%")
print("Cantidad max. de retries: ", MAX_RETRIES)

print("Retries:", retry_count)
print("DLQ:", dlq_count)

print("Failures:", failures)
print("Recoveries:", recoveries)
print(f"Recovery Rate: {round(recovery_rate*100,2)}%")
