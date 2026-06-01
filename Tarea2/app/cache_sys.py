#### se pide EVICTION RATE como evictions / min

from collections import OrderedDict # Para facilitar hacer la politica LRU
import time # Para throughput
import json

def result_size(value): # Para obtener el tamaño de consultas en bytes
    return len(
        json.dumps(value).encode()
    )

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
    # Definir temporalmente la capacidad de almacenar 1 MB, para probar. ttl = 0.01
    def __init__(self, capacity_mb=10, ttl=1):
        self.capacity_mb = capacity_mb
        self.capacity_bytes = capacity_mb * 1024 * 1024

        self.ttl = ttl
        self.expirations = 0

        self.current_bytes = 0
        self.cache = {}
        self.queue = []

        self.hits = 0
        self.misses = 0
        self.evictions = 0

        self.latencies = []

    def get(self,key):
        if key not in self.cache:
            self.misses += 1
            return None

        value,timestamp = self.cache[key]

        if time.time() - timestamp > self.ttl: #  Verificar TTL
            del self.cache[key]
            
            if key in self.queue:
                self.queue.remove(key)

            self.expirations += 1
            self.misses += 1
            return None

        self.hits += 1

        return value
    
    def put(self,key,value): # Ingresar query a cache
        if key in self.cache:
            return
        item_size = result_size(value)

        while self.current_bytes + item_size > self.capacity_bytes: # Verificar si cache esta lleno
            oldest = self.queue.pop(0) # Ultima query en cache sera removida
            old_value = self.cache[oldest]

            self.current_bytes -= result_size(old_value)
            del self.cache[oldest] # Ultima query en cache sera removida
            self.evictions += 1

        self.cache[key] = (value, time.time())
        self.queue.append(key)

        self.current_bytes += item_size

    def execute(self,key,query_function,*args): # Agrupar funciones para simular ejecucion
        t0=time.perf_counter() # Tiempo inicial, para medir latencia

        result = self.get(key)
        if result is None:
            result = query_function(*args)
            payload = { # Aumenta el tamaño de la consulta de forma sintetica (agrega 500KB)
                "result": result,
                "padding": "x"*500000
            }
            self.put(key,payload)

        #result = query_function(*args)
        #self.put(key,result)


        latency=time.perf_counter()-t0 # Latencia
        self.latencies.append(latency)

        return result
    
    def show_metrics(self): # Mostrar metricas
        print("Capacidad de almacenamiento:", self.capacity_mb,"MB")
        print("Cache usado (current):",self.current_bytes/(1024*1024),"MB")
        print("Hits: ", self.hits)
        print("Misses: ", self.misses)
        total = self.hits + self.misses
        if total == 0:
            print("Error al calcular Hit Rate")
        else:
            print(f"Eviction Rate: {round(self.evictions/total, 4)*100}%") # Cantidad de queries removidas de cache
            print(f"Hit Rate: {round(self.hits/total, 4)*100}%")

        latencia_prom = sum(self.latencies)/len(self.latencies)
        print("Latencia promedio:",round(latencia_prom, 6),"segundos")
        print("Consultas expiradas por TTL: ", self.expirations)

        #print("===========LATENCIAS===========")
        #print(self.latencies) 
        #print("===============================")

        
        
# Politica de remocion LRU

class LRUCache:
    def __init__(self, capacity_mb=10, ttl=1):
        self.capacity_mb = capacity_mb
        self.capacity_bytes = capacity_mb * 1024 * 1024

        self.ttl = ttl
        self.expirations = 0

        self.current_bytes = 0
        self.cache = OrderedDict()

        self.hits = 0
        self.misses = 0
        self.evictions = 0

        self.latencies = []
    
    def get(self,key):
        if key not in self.cache:
            self.misses += 1
            return None

        value,timestamp = self.cache[key]

        if time.time()-timestamp > self.ttl: # Verificar TTL
            self.expirations += 1
            del self.cache[key]
            self.misses +=1

            return None

        self.hits +=1
        self.cache.move_to_end(key)

        return value
    
    def put(self,key,value):
        if key in self.cache:
            self.cache.move_to_end(key) # actualizar y marcar como reciente
            self.cache[key] = (value, time.time())
            return

        item_size = result_size(value)

        while self.current_bytes + item_size > self.capacity_bytes: 

            oldest, old_value = self.cache.popitem(last=False) # elimina el menos recientemente usado

            self.current_bytes -= result_size(old_value)

            self.evictions += 1

        self.cache[key] = (value, time.time())

        self.current_bytes += item_size


    def execute(self, key, query_function, *args):
        t0=time.perf_counter() # Tiempo inicial, para medir latencia
        result = self.get(key)

        if result is None:
            result = query_function(*args)
            payload = { # Aumenta el tamaño de la consulta de forma sintetica (agrega 500KB)
                "result": result,
                "padding": "x"*500000
            }
            self.put(key,payload)

        #result = query_function(*args)

        #self.put(key, result)

        latency=time.perf_counter()-t0 # Latencia
        self.latencies.append(latency)

        return result
    
    def show_metrics(self): # Mostrar metricas
        print("Capacidad de almacenamiento:", self.capacity_mb,"MB")
        print("Cache usado (current):",self.current_bytes/(1024*1024),"MB")
        print("Hits: ", self.hits)
        print("Misses: ", self.misses)
        total = self.hits + self.misses
        if total == 0:
            print("Error al calcular Hit Rate")
        else:
            print(f"Eviction Rate: {round(self.evictions/total, 4)*100}%") # Cantidad de queries removidas de cache
            print(f"Hit Rate: {round(self.hits/total, 4)*100}%")

        latencia_prom = sum(self.latencies)/len(self.latencies)
        print("Latencia promedio:",round(latencia_prom, 6),"segundos")
        print("Consultas expiradas por TTL: ", self.expirations)

        #print("===========LATENCIAS===========")
        #print(self.latencies) 
        #print("===============================")

        
     