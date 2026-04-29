print("Prueba del sistema...")
import redis
import json
from traffic_gen import generate_zipf, generate_uniform
from queries import *


r = redis.Redis(
   host="cache",
   port=6379,
   decode_responses=True
)

def main():

    consultas = generate_zipf(100)

    for c in consultas:

        r.rpush(
          "cola:consultas",
          json.dumps(c)
        )

        print("Enviada:",c)

if __name__=="__main__":
    main()
