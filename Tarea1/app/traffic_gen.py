import numpy as np
import random
import time

# Trafico Zipf 
# => Unas zonas mas frecuentes que otras
zonas = ["Z1","Z2","Z3","Z4","Z5"]
tipos = ["Q1","Q2","Q3","Q4","Q5"]


init_time = 0
final_time = 0

# Funciones para Redis

def generate_uniform(n):
    consultas=[]

    for _ in range(n):
        tipo=random.choice(tipos)

        consulta={
            "tipo":tipo,
            "zona":random.choice(zonas)
        }

        if tipo=="Q4":
            otras = [
                z for z in zonas
                if z != consulta["zona"]
                ]
            consulta["zona_b"]=random.choice(otras)

        if tipo in ["Q1","Q2","Q3","Q4"]:
            consulta["confidence_min"]=random.choice(
               [0.0,0.5,0.8]
            )

        if tipo=="Q5":
            consulta["bins"]=5

        consultas.append(consulta)

    return consultas

def generate_zipf(n, a=1.5):
    consultas=[]

    weights=np.array(
        [1/(i**a) for i in range(1,6)]
    )

    weights /= weights.sum()

    for _ in range(n):

        zona = str(np.random.choice(
            zonas,
            p=weights
        ))

        tipo = random.choice(tipos)

        consulta = {
            "tipo": tipo,
            "zona": zona
        }

        if tipo=="Q4":
            otras = [z for z in zonas if z != zona] # Evita comparar con misma zona
            consulta["zona_b"] = random.choice(otras)

        if tipo in ["Q1","Q2","Q3","Q4"]:
            consulta["confidence_min"] = random.choice(
                [0.0,0.5,0.8]
            )

        if tipo=="Q5":
            consulta["bins"] = 5

        consultas.append(consulta)

    return consultas

# # # # # # # # # # # # # # # # # #

# Default (para probar) n=100 "consultas" y a=1.5 "sesgo"
# (entre mas alto mayor sea "a" la diferencia de las prob de zona (z1 -> 70%, z2 -> 20%, z3 -> 8%...))

def generate_zipf_queries(n=100, a=1.5):
    global init_time, final_time
    init_time = time.perf_counter()
    queries = []
    for _ in range(n):
        rank = np.random.zipf(a)
        # forzar a que caiga entre 1 y 5
        rank = ((rank-1) % 5)

        queries.append(zonas[rank])
    final_time = time.perf_counter() - init_time
    return queries


# Trafico uniforme
def generate_uniform_queries(n=100):
    global init_time, final_time
    init_time = time.perf_counter()
    queries = random.choices(zonas,k=n)
    final_time = time.perf_counter() - init_time
    return queries

def gen_time():
    global final_time
    print("Tiempo en generar datos: ", final_time)
