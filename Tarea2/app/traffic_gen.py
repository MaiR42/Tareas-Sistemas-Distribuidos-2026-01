import numpy as np
import random


# Trafico Zipf 
# => Unas zonas mas frecuentes que otras
zonas = ["Z1","Z2","Z3","Z4","Z5"]
tipos = ["Q1","Q2","Q3","Q4","Q5"]

# # # # # # # # # # # # # # # # # #

# Default (para probar) n=100 "consultas" y a=1.5 "sesgo"
# (entre mas alto mayor sea "a" la diferencia de las prob de zona (z1 -> 70%, z2 -> 20%, z3 -> 8%...))

def generate_zipf_queries(n=1, a=1.5):
    queries = []
    for _ in range(n):
        rank = np.random.zipf(a)
        # forzar a que caiga entre 1 y 5
        rank = ((rank-1) % 5)

        queries.append(zonas[rank])
    return queries


# Trafico uniforme
def generate_uniform_queries(n=1):
    queries = random.choices(zonas,k=n)
    return queries


# Para el Redis
def generate_query(distribution="zipf"): #distribution: "zipf" o "uniform"
    
    if distribution == "zipf":
        zona = generate_zipf_queries(1)[0]
    elif distribution == "uniform":
        zona = generate_uniform_queries(1)[0]
    else:
        raise ValueError("distribution debe ser 'zipf' o 'uniform'")

    tipo = random.choice(tipos)
    consulta = {
        "tipo": tipo,
        "zona": zona
    }

    if tipo == "Q4":
        otras = [z for z in zonas if z != zona]
        consulta["zona_b"] = random.choice(otras)

    if tipo in ["Q1", "Q2", "Q3", "Q4"]:
        consulta["confidence_min"] = random.choice([0.0, 0.5, 0.8])

    if tipo == "Q5":
        consulta["bins"] = 5

    return consulta