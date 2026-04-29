print("Prueba del sistema...")

import time
from queries import q1_count, q2_area, q3_density, q4_compare, q5_confidence_dist
from traffic_gen import generate_uniform_queries, generate_zipf_queries, gen_time
from cache_sys import cached_query, show_metricas, FIFOCache, LRUCache

# # # # # # # # # # # # # # # # # # # # # # # # # # # # 

print("==================PRUEBA FIFO==================")

init_time = 0
final_time = 0

init_time = time.perf_counter()

cache = FIFOCache()

for zone in generate_uniform_queries():

    result = cache.execute(
        f"count:{zone}",
        q1_count,
        zone
    )

final_time = time.perf_counter() - init_time
print("Tiempo en simular cache: ", final_time)
gen_time()
print(cache.show_metrics())

print("==================PRUEBA FIFO (zipf)==================")

init_time = 0
final_time = 0

init_time = time.perf_counter()

cache = FIFOCache()

for zone in generate_zipf_queries():

    result = cache.execute(
        f"count:{zone}",
        q1_count,
        zone
    )

final_time = time.perf_counter() - init_time
print("Tiempo en simular cache: ", final_time)
gen_time()
print(cache.show_metrics())

# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
print("==================PRUEBA LRU==================")
init_time = time.perf_counter()
cache = LRUCache()

for zone in generate_uniform_queries():

    result = cache.execute(
        f"count:{zone}",
        q1_count,
        zone
    )
final_time = time.perf_counter() - init_time
print("Tiempo en simular cache: ", final_time)
gen_time()
print(cache.show_metrics())
