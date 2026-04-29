from collections import OrderedDict # Para facilitar hacer la politica LRU
import time # Para throughput

cache = {}

hits = 0 # Consultas que estan en cache
misses = 0 # Consultas que no estan en cache => buscar en backend
hit_rate = 0

# Cache infinito, para probar
def cached_query(query_key, query_function, *args):
    global hits, misses

    if query_key in cache:
        hits += 1
        print("HIT")
        return cache[query_key]

    misses += 1
    print("MISS")

    result = query_function(*args)

    cache[query_key] = result

    return result

def show_metricas():
    print("Hits: ", hits)
    print("Misses: ", misses)

    if (hits + misses) == 0:
        print("Error al calcular Hit Rate")
    else:
            hit_rate = hits/(hits+misses) # hits/total
            print("Hit Rate: ", hit_rate)

# Politica de remocion FIFO
class FIFOCache:
    # Definir temporalmente la capacidad de almacenar queries en 3, para probar
    def __init__(self, capacity=3):

        self.capacity = capacity

        self.cache = {}

        self.queue = []

        self.hits = 0
        self.misses = 0
        self.evictions = 0

        self.latencies = []

    def get(self,key): 
        if key in self.cache: # Verificar si query esta en cache
            self.hits += 1
            return self.cache[key]

        self.misses += 1
        return None
    
    def put(self,key,value): # Ingresar query a cache
        if key in self.cache:
            return
        if len(self.cache) >= self.capacity: # Verificar si cache esta lleno
            oldest = self.queue.pop(0) # Ultima query en cache sera removida
            del self.cache[oldest]
            self.evictions += 1

        self.cache[key] = value
        self.queue.append(key)

    def execute(self,key,query_function,*args): # Agrupar funciones para simular ejecucion
        t0=time.perf_counter() # Tiempo inicial, para medir latencia

        result = self.get(key)
        if result is not None:
            return result

        result = query_function(*args)
        self.put(key,result)


        latency=time.perf_counter()-t0 # Latencia
        self.latencies.append(round(latency, 4))

        return result
    
    def show_metrics(self): # Mostrar metricas
        print("Capacidad de almacenamiento:", self.capacity,"queries")
        print("Hits: ", self.hits)
        print("Misses: ", self.misses)
        total = self.hits + self.misses
        if total == 0:
            print("Error al calcular Hit Rate")
        else:
            print(f"Eviction Rate: {round(self.evictions/total, 4)*100}%") # Cantidad de queries removidas de cache
            print(f"Hit Rate: {round(self.hits/total, 4)*100}%")

        latencia_prom = sum(self.latencies)/len(self.latencies)
        print("Latencia promedio:",round(latencia_prom, 4),"segundos")
        print(self.latencies) 
        


class LRUCache:
    def __init__(self, capacity=3):

        self.capacity = capacity

        self.cache = OrderedDict()

        self.hits = 0
        self.misses = 0
        self.evictions = 0

        self.latencies = []
    
    def get(self, key):
        if key not in self.cache: # Verificar si query no esta en cache
            self.misses += 1
            return None

        self.hits += 1
        self.cache.move_to_end(key) # mover al final => mas reciente

        return self.cache[key]
    
    def put(self, key, value):

        if key in self.cache:
            # actualizar y marcar como reciente
            self.cache.move_to_end(key)
            self.cache[key] = value
            return

        if len(self.cache) >= self.capacity:

            # elimina el menos recientemente usado
            oldest, _ = self.cache.popitem(last=False)

            self.evictions += 1

        self.cache[key] = value

    def execute(self, key, query_function, *args):
        t0=time.perf_counter() # Tiempo inicial, para medir latencia
        result = self.get(key)

        if result is not None:
            return result

        result = query_function(*args)

        self.put(key, result)

        latency=time.perf_counter()-t0 # Latencia
        self.latencies.append(round(latency, 4))

        return result
    
    def show_metrics(self): # Mostrar metricas
        print("Capacidad de almacenamiento:", self.capacity,"queries")
        print("Hits: ", self.hits)
        print("Misses: ", self.misses)
        total = self.hits + self.misses
        if total == 0:
            print("Error al calcular Hit Rate")
        else:
            print(f"Eviction Rate: {round(self.evictions/total, 4)*100}%") # Cantidad de queries removidas de cache
            print(f"Hit Rate: {round(self.hits/total, 4)*100}%")

        latencia_prom = sum(self.latencies)/len(self.latencies)
        print("Latencia promedio:",round(latencia_prom, 4),"segundos")
        print(self.latencies) 
     
