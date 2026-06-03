# Para facilitar el uso de variables y parametros
# Politica de remocion, espacio de memoria cache y TRAFFIC_INTERVAL sigue en el docker-compose.yml
DEBUG = False

# T1
TTL = 10
GEN_TRAFIC_DISTR = "zipf" # "zipf" o "uniform" # main.py

# T2
MAX_RETRIES = 2 # consumer_fakfa.py     # PROBANDO CON 2, 5
FAILURE_RATE = 0.5 # Prob. de simular fallas en misses # consumer_kafka.py      # PROBANDO CON 0.1, 0.5, 0.9

PROD_QUERY_QUANTITY = 500 # Cantidad de queries que manda un producer # producer_kafka.py








# Variables para las metricas en el CSV
CONSUMERS = 2
# Del docker-compose.yml
CACHE_REMOTION_POLITIC = "allkeys-lru"
CACHE_MEMORY = "2mb"
