import numpy as np
import random
import time

# Trafico Zipf 
# => Unas zonas mas frecuentes que otras
zones = ["Z1","Z2","Z3","Z4","Z5"]

# Default (para probar) n=100 "consultas" y a=1.5 "sesgo"
# (entre mas alto mayor sea "a" la diferencia de las prob de zona (z1 -> 70%, z2 -> 20%, z3 -> 8%...))

init_time = 0
final_time = 0

def generate_zipf_queries(n=100, a=1.5):
    global init_time, final_time
    init_time = time.perf_counter()
    queries = []
    for _ in range(n):
        rank = np.random.zipf(a)
        # forzar a que caiga entre 1 y 5
        rank = ((rank-1) % 5)

        queries.append(zones[rank])
    final_time = time.perf_counter() - init_time
    return queries


# Trafico uniforme
def generate_uniform_queries(n=100):
    global init_time, final_time
    init_time = time.perf_counter()
    queries = random.choices(zones,k=n)
    final_time = time.perf_counter() - init_time
    return queries

def gen_time():
    global final_time
    print("Tiempo en generar datos: ", final_time)
