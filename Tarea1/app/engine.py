import redis
import json

from queries import (
    q1_count,
    q2_area,
    q3_density,
    q4_compare,
    q5_confidence_dist
)

r = redis.Redis(
    host="localhost",   # o cache en docker
    port=6379,
    decode_responses=True
)


hits=0
misses=0


def procesar(c):

    if c["tipo"]=="Q1":
        return q1_count(
            c["zona"],
            c["confidence_min"]
        )

    elif c["tipo"]=="Q2":
        return q2_area(
            c["zona"],
            c["confidence_min"]
        )

    elif c["tipo"]=="Q3":
        return q3_density(
            c["zona"],
            c["confidence_min"]
        )

    elif c["tipo"]=="Q4":
        return q4_compare(
            c["zona"],
            c["zona_b"],
            c["confidence_min"]
        )

    elif c["tipo"]=="Q5":
        return q5_confidence_dist(
            c["zona"],
            c["bins"]
        )


def main():

    global hits,misses

    print("Esperando consultas...")

    while True:

        msg = r.blpop(
            "cola:consultas"
        )

        consulta = json.loads(
            msg[1]
        )

        cache_key = json.dumps(
            consulta,
            sort_keys=True
        )

        cached = r.get(cache_key)

        if cached:

            hits +=1

            print("HIT", consulta)

        else:

            misses +=1

            print("MISS", consulta)

            resultado = procesar(
                consulta
            )

            r.set(
                cache_key,
                json.dumps(resultado),
                ex=60   # TTL ajustado a 60 segundos
            )

        print(
            "Hit rate:",
            hits/(hits+misses)
        )


if __name__=="__main__":
    main()
