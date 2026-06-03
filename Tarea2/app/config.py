# Para facilitar el uso de variables y parametros
# Politica de remocion, espacio de memoria cache y TRAFFIC_INTERVAL sigue en el docker-compose.yml

# T1
TTL = 10
GEN_TRAFIC_DISTR = "zipf" # "zipf" o "uniform" # main.py

# T2

DEBUG = False # Para mostrar los prints principalmente

MAX_RETRIES = 2 # consumer_fakfa.py
FAILURE_RATE = 0.7 # Prob. de simular fallas en misses # consumer_kafka.py
PROD_QUERY_QUANTITY = 10000 # Cantidad de queries que manda un producer # producer_kafka.py
