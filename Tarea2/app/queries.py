# !!! No tocar para Tarea2 !!!
from data_load import data
from data_load import zones

from statistics import mean # Para usar "mean" en Q2 
import math
from numpy import histogram # Para Q5

# Q1
def q1_count(zone_id, confidence_min=0.0):
    records = data[zone_id]
    return sum(
        1 for _, r in records.iterrows() # Para usar r["confidence"]
        if r["confidence"] >= confidence_min
    )

# Q2
def q2_area(zone_id, confidence_min = 0.0):
    areas = [r["area_in_meters"] for _, r in data[zone_id].iterrows() if r["confidence"] >= confidence_min] # Cambie el formato del for para usar r["confidence"]
    return {
        "avg_area": mean(areas), "total_area": sum(areas), "n": len(areas) # Quizas limitar decimales de "avg_areas" y "total_area" 
    }

# Q3
zone_area_km2 = {}

# Calcular area de cada zona
for zone_id,(lat_min,lat_max,lon_min,lon_max) in zones.items():
    lat_km = (lat_max - lat_min) * 111
    mean_lat = math.radians((lat_max + lat_min)/2)

    lon_km = (lon_max - lon_min) * 111 * math.cos(mean_lat)
    zone_area_km2[zone_id] = abs(lat_km * lon_km)

def q3_density(zone_id, confidence_min=0.0):
    count = q1_count(zone_id, confidence_min)
    area_km2 = zone_area_km2[zone_id] # rea precalculada de la bbox
    return count / area_km2

# Q4
def q4_compare (zone_a ,zone_b ,confidence_min =0.0):
    da = q3_density ( zone_a , confidence_min )
    db = q3_density ( zone_b , confidence_min )
    return { "zone_a" : da , "zone_b" : db , "winner" : zone_a if da > db else zone_b }

# Q5
def q5_confidence_dist(zone_id, bins=5):
    scores = data[zone_id]["confidence"]
    counts, edges = histogram(scores, bins=bins, range=(0,1))

    return [
        {"bucket": i, "min": float(edges[i]), "max": float(edges[i+1]),
            "count": int(counts[i])} for i in range(bins)]
