# Solamente para mostrar las metricas

import redis
import numpy as np

r = redis.Redis(host="cache", port=6379, decode_responses=True)

stats = r.info('stats')

hits = int(r.get("metrics:hits") or 0)
misses = int(r.get("metrics:misses") or 0)
lat = [float(x) for x in r.lrange("metrics:latency", 0, -1)]
eviction = int(r.get("metrics:evicted_keys") or 0)
total = hits + misses
hit_rate = 0

if total != 0:
    hit_rate = hits/total

p50 = np.percentile(lat, 50) if lat else 0
p95 = np.percentile(lat, 95) if lat else 0

# Evictions
info = r.info("stats")
mem_info = r.info('memory')

evicted_keys = info.get("evicted_keys", 0)
capacity = r.config_get("maxmemory")
used_memory_bytes = mem_info.get("used_memory", 0)

print("Hits:", hits)
print("Misses:", misses)
print(f"Hit rate: {round(hit_rate*100, 4)}%")
print("Evicted keys: ", evicted_keys)
print("p50:", p50)
print("p95:", p95)

print(f"Capacidad: {int(capacity['maxmemory']) / (1024*1024)} MB")
print(f"Memoria usada en cache: {used_memory_bytes / (1024*1024)} MB")
