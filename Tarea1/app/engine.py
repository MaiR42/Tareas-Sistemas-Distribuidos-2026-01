import os
import redis
import json
import time

from queries import (
    q1_count,
    q2_area,
    q3_density,
    q4_compare,
    q5_confidence_dist,
)

# Para Redis (IMPORTANTE: host="cache")
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "cache"),
    port=6379,
    decode_responses=True
)

TTL_SECONDS = int(os.getenv("CACHE_TTL", 60)) # TTL (por default 60 segundos)

print("Worker iniciado, esperando consultas...")

# -------- MÉTRICAS --------
def record_hit():
    r.incr("metrics:hits")

def record_miss():
    r.incr("metrics:misses")

def record_latency(value):
    r.rpush("metrics:latency", value)

def record_request():
    r.incr("metrics:requests")


# -------- LOOP PRINCIPAL --------
while True:
    item = r.blpop("cola:consultas", timeout=5)
    print("Item recibido:", item)
    if item is None:
        print("Esperando consultas...")
        continue

    _, raw = item
    start = time.time()

    record_request()

    query = json.loads(raw)

    qtype = query["type"]
    params = query["params"]
    cache_key = query["cache_key"]

    cached = r.get(cache_key)

    if cached:
        print(f"[CACHE HIT] {cache_key}")
        record_hit()

        latency = time.time() - start
        record_latency(latency)
        continue

    print(f"[CACHE MISS] {cache_key}")
    record_miss()

    # -------- EJECUCIÓN --------
    if qtype == "Q1":
        result = q1_count(**params)
    elif qtype == "Q2":
        result = q2_area(**params)
    elif qtype == "Q3":
        result = q3_density(**params)
    elif qtype == "Q4":
        result = q4_compare(**params)
    elif qtype == "Q5":
        result = q5_confidence_dist(**params)
    else:
        result = {"error": "Unknown query type"}

    # -------- CACHE CON TTL --------
    r.setex(cache_key, TTL_SECONDS, json.dumps(result))

    latency = time.time() - start
    record_latency(latency)

    print(f"Guardado en cache: {cache_key}")

    print("=============")
    print()
