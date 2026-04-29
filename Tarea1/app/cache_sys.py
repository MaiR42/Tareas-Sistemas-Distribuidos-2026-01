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
        result = self.get(key)
        if result is not None:
            return result

        result = query_function(*args)
        self.put(key,result)

        return result
    
    def show_metrics(self): # Mostrar metricas
        print("Capacidad de almacenamiento:", self.capacity,"queries")
        print("Hits: ", self.hits)
        print("Misses: ", self.misses)
        print("Evictions: ", self.evictions) # Cantidad de accesos a backend

        if (self.hits + self.misses) == 0:
            print("Error al calcular Hit Rate")
        else:
            hit_rate = self.hits / (self.hits + self.misses)
            print("Hit Rate: ", hit_rate)
        
