# Solamente para mostrar las metricas

import redis
import numpy as np

r = redis.Redis(host="cache", port=6379, decode_responses=True)

hits = int(r.get("metrics:hits") or 0)
misses = int(r.get("metrics:misses") or 0)
lat = [float(x) for x in r.lrange("metrics:latency", 0, -1)]

total = hits + misses
hit_rate = 0

if total != 0:
    hit_rate = hits/total

p50 = np.percentile(lat, 50) if lat else 0
p95 = np.percentile(lat, 95) if lat else 0

print("Hits:", hits)
print("Misses:", misses)
print(f"Hit rate: {round(hit_rate*100, 4)}%")
print("p50:", p50)
print("p95:", p95)
