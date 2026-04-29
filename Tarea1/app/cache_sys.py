cache = {}

hits = 0 # Consultas que estan en cache
misses = 0 # Consultas que no estan en cache => buscar en backend
hit_rate = 0

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
