# Para generar trafico
import os
import json
import time
import redis

from traffic_gen import generate_query

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "cache"),
    port=6379,
    decode_responses=True
)

distribution = os.getenv("TRAFFIC_DIST", "zipf")
interval = float(os.getenv("TRAFFIC_INTERVAL", "1"))

print(f"Generador iniciado con distribución: {distribution}")


def build_payload(q):
    tipo = q["tipo"]

    # -------- PARAMS --------
    if tipo in ["Q1", "Q2", "Q3"]:
        params = {
            "zone_id": q["zona"],
            "confidence_min": q.get("confidence_min", 0.0)
        }

    elif tipo == "Q4":
        params = {
            "zone_a": q["zona"],
            "zone_b": q["zona_b"],
            "confidence_min": q.get("confidence_min", 0.0)
        }

    elif tipo == "Q5":
        params = {
            "zone_id": q["zona"],
            "bins": q.get("bins", 5)
        }

    else:
        params = {}

    # -------- CACHE KEY --------
    if tipo == "Q1":
        key = f"count:{params['zone_id']}:conf={params.get('confidence_min', 0.0)}"

    elif tipo == "Q2":
        key = f"area:{params['zone_id']}:conf={params.get('confidence_min', 0.0)}"

    elif tipo == "Q3":
        key = f"density:{params['zone_id']}:conf={params.get('confidence_min', 0.0)}"

    elif tipo == "Q4":
        key = f"compare:density:{params['zone_a']}:{params['zone_b']}:conf={params.get('confidence_min', 0.0)}"

    elif tipo == "Q5":
        key = f"confidence_dist:{params['zone_id']}:bins={params.get('bins', 5)}"

    else:
        key = "unknown"

    return {
        "type": tipo,
        "params": params,
        "cache_key": key
    }


def main():
    while True:
        raw_query = generate_query(distribution=distribution)

        payload = build_payload(raw_query)

        r.rpush("cola:consultas", json.dumps(payload))

        print(f"Enviada: Tipo: {payload['type']}, Cache_key: {payload['cache_key']}")

        time.sleep(interval)


if __name__ == "__main__":
    main()
