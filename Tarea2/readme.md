# Tarea 2 - Sistemas Distribuidos 2026-1
## Procesamiento Asíncrono y Tolerancia a Fallos con Apache Kafka

**Universidad Diego Portales**  
Curso: Sistemas Distribuidos  
Profesor: Nicolás Hidalgo  
Integrantes: Mair Escobar — Martín Quintana

---

## Descripción

Sistema de procesamiento asíncrono de consultas geoespaciales sobre el dataset **Google Open Buildings** (Región Metropolitana de Santiago), incorporando Apache Kafka como capa de mensajería entre el Generador de Tráfico y el procesamiento de consultas.

El sistema implementa:
- Procesamiento asíncrono con Kafka Producer/Consumer
- Sistema de reintentos mediante tópicos Kafka
- Dead Letter Queue (DLQ) para consultas irresolubles
- Caché en Redis con política LRU
- Métricas experimentales exportadas a CSV
- Escalamiento horizontal con múltiples consumers

---

## Requisitos

- Docker
- Docker Compose
- Python 3.11+

---

## Estructura del Proyecto

```
Tarea2/
├── app/
│   ├── config.py           # Parámetros del sistema
│   ├── consumer_kafka.py   # Consumer Kafka con reintentos y DLQ
│   ├── producer_kafka.py   # Producer Kafka
│   ├── traffic_gen.py      # Generador de tráfico (Zipf/Uniforme)
│   ├── queries.py          # Queries Q1-Q5 sobre el dataset
│   ├── data_load.py        # Carga del dataset geoespacial
│   ├── metrics.py          # Métricas y exportación a CSV
│   ├── engine.py           # Worker síncrono (Tarea 1, referencia)
│   └── results/
│       └── results.csv     # Resultados experimentales
├── data/
│   └── 967_buildings.csv.gz
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Configuración

Los parámetros del sistema se configuran en `app/config.py`:

| Parámetro | Descripción | Default |
|---|---|---|
| `TTL` | Tiempo de vida del caché (segundos) | 10 |
| `MAX_RETRIES` | Máximo de reintentos antes de DLQ | 2 |
| `FAILURE_RATE` | Probabilidad de falla simulada | 0.5 |
| `PROD_QUERY_QUANTITY` | Consultas por ejecución del producer | 10000 |
| `GEN_TRAFIC_DISTR` | Distribución de tráfico (`zipf` o `uniform`) | `zipf` |
| `CONSUMERS` | Número de consumers (para el CSV) | 1 |

El tamaño de caché y política de remoción se configuran en `docker-compose.yml`:
```yaml
command:
  - redis-server
  - --maxmemory
  - 2mb
  - --maxmemory-policy
  - allkeys-lru
```

---

## Cómo ejecutar

### 1. Levantar los servicios

```bash
docker-compose up --build
```

Esto levanta: Zookeeper, Kafka, Redis y la aplicación.

### 2. Ejecutar el Consumer (en una terminal)

```bash
docker exec -it tarea2_app python consumer_kafka.py
```

Para múltiples consumers (en terminales separadas):

```bash
docker exec -it tarea2_app python consumer_kafka.py
docker exec -it tarea2_app python consumer_kafka.py
```

### 3. Ejecutar el Producer (en otra terminal)

```bash
docker exec -it tarea2_app python producer_kafka.py
```

### 4. Ver métricas y exportar CSV

```bash
docker exec -it tarea2_app python metrics.py
```

### 5. Apagar el sistema

```bash
docker-compose down -v
```

> **Importante:** Usar `down -v` para limpiar los volúmenes de Kafka y Redis entre experimentos.

---

## Flujo del Sistema

```
Generador de Tráfico
        ↓
   Kafka Producer
        ↓
   Tópico: consultas
        ↓
  Kafka Consumer(s)
        ↓
   ┌────────────┐
   │ Cache Hit? │
   └────────────┘
      ↙       ↘
    Sí          No
    ↓            ↓
 Retornar    Procesar
 resultado   consulta
                ↓
          ┌──────────┐
          │  ¿Falla? │
          └──────────┘
            ↙      ↘
           No       Sí
           ↓         ↓
        Guardar   retries++
        en caché      ↓
                ¿retries <= MAX_RETRIES?
                  ↙              ↘
                 Sí               No
                 ↓                 ↓
          consultas_retry    consultas_dlq
                                 (DLQ)
```

---

## Tópicos Kafka

| Tópico | Descripción |
|---|---|
| `consultas` | Tópico principal — consultas nuevas |
| `consultas_retry` | Consultas que fallaron y se reintentarán |
| `consultas_dlq` | Dead Letter Queue — consultas irresolubles |

---

## Métricas Registradas

| Métrica | Descripción |
|---|---|
| Throughput | Consultas procesadas por segundo |
| Queue delay | Tiempo promedio en cola |
| Retry rate | Fracción de consultas reenviadas a reintento |
| Recovery rate | Fracción de consultas recuperadas tras fallo |
| DLQ rate | Fracción de consultas enviadas a la DLQ |
| Backlog size | Mensajes pendientes en Kafka |
| Recovery time | Tiempo entre primera falla y recuperación |
| Hit rate | Fracción de consultas resueltas por caché |

Los resultados se exportan automáticamente a `app/results/results.csv`.

---

## Escenarios Evaluados

1. **Sistema Base** — Arquitectura síncrona de Tarea 1 (sin Kafka)
2. **Kafka + 1 Consumer** — FAILURE_RATE ∈ {10%, 50%, 90%}
3. **Kafka + 2 Consumers** — Comparación de escalamiento horizontal
4. **Falla Temporal** — FAILURE_RATE = 90%, evaluación de backlog
5. **Reintentos** — MAX_RETRIES ∈ {2, 5}
6. **Spike de Tráfico** — 10.000 consultas publicadas de forma inmediata

---

## Referencias

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Redis Documentation](https://redis.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Confluent Platform Documentation](https://docs.confluent.io/)
- [Repositorio Tarea 1](https://github.com/MaiR42/Tareas-Sistemas-Distribuidos-2026-01/tree/main/Tarea1)
