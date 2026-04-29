import os
import redis
import json

from queries import (
    q1_count,
    q2_area,
    q3_density,
    q4_compare,
    q5_confidence_dist,
)

# Conexión correcta a Redis dentro de Docker
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "cache"),
    port=6379,
    decode_responses=True
)


r.set("prueba","hola",ex=60)
print(r.get("prueba"))


print("Esperando consultas...")

while True:
    _, raw = r.blpop("cola:consultas")
    query = json.loads(raw)

    qtype = query["type"]
    params = query["params"]

    cache_key = query["cache_key"]

    # Revisar caché
    cached = r.get(cache_key)
    if cached:
        print(f"[CACHE HIT] {cache_key}")
        continue

    print(f"[CACHE MISS] {cache_key}")

    # Ejecutar consulta
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

    # Guardar en caché (con TTL si quieres después)
    r.set(cache_key, json.dumps(result))

    print(f"Resultado guardado en cache: {cache_key}")
