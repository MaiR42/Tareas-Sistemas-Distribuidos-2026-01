import pandas as pd

df = pd.read_csv(
    "./data/967_buildings.csv.gz",
    usecols=["latitude","longitude","area_in_meters","confidence"] # Por el momento solo importar eso
)

# Debug

#print(df.head())
#print(df.columns)
#print(df.shape)

zones = {
# Zone ID # lat_min # lat_max # lon_min# lon_max
    "Z1": (-33.445,-33.420,-70.640,-70.600),
    "Z2": (-33.420,-33.390,-70.600,-70.550),
    "Z3": (-33.530,-33.490,-70.790,-70.740),
    "Z4": (-33.460,-33.430,-70.670,-70.630),
    "Z5": (-33.470,-33.430,-70.810,-70.760)
}

def data(zone_id):
    lat_min, lat_max, lon_min, lon_max = zones[zone_id]

    return df[
      (df["latitude"] >= lat_min) &
      (df["latitude"] <= lat_max) &
      (df["longitude"] >= lon_min) &
      (df["longitude"] <= lon_max)
    ]


# Debug
#z1 = get_zone_buildings("Z1")
#print(len(z1))

# # # Consultas # # #
from statistics import mean # Para usar ".mean()" en q2 

def q1_count(zone_id, confidence_min=0.0):
    records = data(zone_id)

    return len(
        records[
            records["confidence"] >= confidence_min
        ])

def q2_area(zone_id, confidence_min=0.0):
    records = data(zone_id)
    areas = records[
        records["confidence"] >= confidence_min
    ]["area_in_meters"]

    return {
       "avg_area": areas.mean(),
       "total_area": areas.sum(),
       "n": len(areas)
    }

# Debug
print(q1_count("Z1"))
print(q1_count("Z1",0.8))