import pandas as pd
from statistics import mean # Para usar "mean" en q2 
import math

# # # Cargar dataset

df = pd.read_csv(
    "./data/967_buildings.csv.gz",
    usecols=["latitude","longitude","area_in_meters","confidence"] # Por el momento solo importar eso
)

# # # Informacion de ubicacion por zona

zones = {
# Zone ID # lat_min # lat_max # lon_min# lon_max
    "Z1": (-33.445,-33.420,-70.640,-70.600),
    "Z2": (-33.420,-33.390,-70.600,-70.550),
    "Z3": (-33.530,-33.490,-70.790,-70.740),
    "Z4": (-33.460,-33.430,-70.670,-70.630),
    "Z5": (-33.470,-33.430,-70.810,-70.760)
}

data = {}

for zone_id, (lat_min,lat_max,lon_min,lon_max) in zones.items():

    data[zone_id] = df[
      (df["latitude"] >= lat_min) &
      (df["latitude"] <= lat_max) &
      (df["longitude"] >= lon_min) &
      (df["longitude"] <= lon_max)
    ]

# # # Consultas

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
        "avg_area": mean(areas), "total_area": sum(areas), "n": len(areas)
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


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def main():
    print("Hoal mundo")
    print("========= Consulas =========")

    print(q1_count("Z1"))
    print(q1_count("Z2"))





if __name__ == "__main__":
    main()
