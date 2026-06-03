# Para facilitar el uso de variables y parametros
# Politica de remocion, espacio de memoria cache y TRAFFIC_INTERVAL sigue en el docker-compose.yml

# T1
TTL = 60 # engine.py
GEN_TRAFIC_DISTR = "zipf" # "zipf" o "uniform" # main.py

# T2
MAX_RETRIES = 3 # retry_manager.py # Despues
FAILURE_RATE = 0.9 # Simular fallas # consumer_kafka.py
PROD_QUERY_QUANTITY = 100 # Cantidad de queries que manda un producer
