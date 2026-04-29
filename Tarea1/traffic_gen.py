import numpy as np
import random

# Trafico Zipf 
# => Unas zonas mas frecuentes que otras
zones = ["Z1","Z2","Z3","Z4","Z5"]

# Default (para probar) n=20 "consultas" y a=1.5 "sesgo"
# (entre mas alto mayor sea "a" la diferencia de las prob de zona (z1 -> 70%, z2 -> 20%, z3 -> 8%...))
def generate_zipf_queries(n=20, a=1.5):
    queries = []
    for _ in range(n):
        rank = np.random.zipf(a)
        # forzar a que caiga entre 1 y 5
        rank = ((rank-1) % 5)

        queries.append(zones[rank])
    return queries


# Trafico uniforme
def generate_uniform_queries(n=20):
    return random.choices(zones,k=n)
