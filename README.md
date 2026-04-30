# Sistema de Evaluación de Cache Distribuida con Redis

## Descripción

Este proyecto implementa un sistema distribuido para analizar el comportamiento de un mecanismo de cache en memoria utilizando Redis. La solución permite ejecutar consultas analíticas sobre un dataset geoespacial, simular distintos patrones de acceso y medir métricas de desempeño bajo condiciones controladas.

El sistema está diseñado para evaluar cómo responde una cache frente a distintos niveles de carga, considerando factores como limitación de memoria, expiración de datos (TTL) y políticas de reemplazo.

---

## Objetivos

### Objetivo General

Evaluar el comportamiento de un sistema de cache distribuido basado en Redis, mediante la ejecución de consultas sobre un dataset geoespacial, analizando su rendimiento bajo distintos patrones de carga y restricciones de memoria.

### Objetivos Específicos

- Implementar un sistema de procesamiento de consultas utilizando una arquitectura distribuida basada en contenedores.
- Integrar Redis como mecanismo de cache en memoria, cola de procesamiento y almacenamiento de métricas.
- Simular tráfico de consultas utilizando distribuciones uniforme y Zipf.
- Analizar métricas como hit rate, latencia, throughput, uso de memoria y evictions.
- Evaluar el impacto de la política de reemplazo LRU bajo limitación de memoria.
- Medir el efecto del TTL en la expiración de datos.
- Comparar el desempeño bajo distintos escenarios de carga.

---

## Arquitectura del Sistema

El sistema sigue una arquitectura distribuida basada en contenedores, donde Redis actúa como componente central.

### Componentes

- Generador de tráfico
- Cola de consultas (Redis)
- Worker de procesamiento
- Sistema de cache (Redis)
- Módulo de métricas
- Dataset geoespacial

### Flujo de funcionamiento

1. Se generan consultas sintéticas.
2. Se envían a Redis (cola).
3. Un worker consume las consultas.
4. Se verifica cache:
   - Hit → respuesta inmediata
   - Miss → ejecución de consulta
5. Se guarda resultado con TTL.
6. Se registran métricas.

### Patrón de diseño

- Cache-aside (lazy loading)
- Arquitectura orientada a eventos

---

## Tecnologías Utilizadas

- Python 3.11
- Redis 7
- Docker
- Docker Compose
- NumPy
- Pandas

---


## Estructura del Proyecto

    app/
    ├── engine.py          # Worker de procesamiento
    ├── main.py            # Generador de tráfico
    ├── traffic_gen.py     # Distribuciones de tráfico
    ├── queries.py         # Consultas analíticas
    ├── data_load.py       # Carga del dataset
    ├── metrics.py         # Métricas del sistema

    data/
    └── 967_buildings.csv.gz  # Dataset geoespacial

    docker-compose.yml
    Dockerfile
    requirements.txt

---

## Instrucciones de Ejecución

1. Levantar contenedores:
docker-compose up --build

2. Generar tráfico:
docker-compose exec app python main.py

3. Ejecutar worker:
docker-compose exec app python engine.py

4. Ver métricas:
docker-compose exec app python metrics.py

---

## Métricas Evaluadas

- Hit Rate
- Miss Rate
- Latencia (p50, p95)
- Throughput
- Uso de memoria
- Evictions
- Expiraciones por TTL

---

## Configuración de Cache

El sistema permite configurar distintos parámetros para evaluar el comportamiento de la caché:

- **Capacidad de memoria:** 2 MB, 4 MB y 8 MB
- **Política de reemplazo:**
  - LRU (Least Recently Used)
  - LFU (Least Frequently Used)
- **TTL (Time To Live):**
  - 60 segundos (configuración base)
  - 20 segundos (escenario de estrés)

Estas configuraciones permiten analizar el impacto de cada parámetro en el rendimiento del sistema.

---

## Dataset

El sistema utiliza el dataset **Google Open Buildings**, filtrado para la Región Metropolitana de Santiago.

Cada registro contiene:

- Latitud
- Longitud
- Área de la edificación (m²)
- Nivel de confianza

Las consultas se realizan sobre zonas geográficas predefinidas, lo que permite simular patrones de acceso realistas.

---

## Tipos de Consultas

El sistema implementa cinco tipos de consultas:

- **Q1:** Conteo de edificaciones por zona
- **Q2:** Área promedio y total
- **Q3:** Densidad de edificaciones
- **Q4:** Comparación entre zonas
- **Q5:** Distribución de confianza

Estas consultas son ejecutadas en memoria y sus resultados son almacenados en caché.

---

## Experimentos Realizados

Los experimentos fueron ejecutados bajo las siguientes condiciones:

- Duración: 10 minutos por escenario
- Intervalo de tráfico: 0.01 segundos
- Distribuciones evaluadas:
  - Uniforme
  - Zipf

Se evaluaron múltiples combinaciones de:
- Tamaño de caché
- Política de reemplazo
- TTL

---

## Resultados Relevantes

A partir de los experimentos realizados, se observó que:

- A mayor memoria, menor cantidad de evictions.
- Con 8 MB de memoria, las evictions desaparecen completamente.
- La política **LFU** presenta mejor rendimiento que LRU en escenarios con alta repetición.
- La distribución **Zipf** favorece el uso de caché.
- Un TTL bajo (20 segundos) reduce significativamente el rendimiento del sistema.

---

## Estado del Proyecto

Proyecto finalizado con implementación completa de:

- Arquitectura distribuida
- Sistema de caché con Redis
- Generación de tráfico sintético
- Métricas de rendimiento
- Análisis experimental

---


---

## Autores

- Mair Escobar
- Martín Quintana

---

## Consideraciones

Este proyecto fue desarrollado con fines académicos para la asignatura de Sistemas Distribuidos.

Todas las decisiones de diseño fueron justificadas y evaluadas mediante experimentación empírica.

