import csv
import numpy as np

lat_min,lat_max=47.2701114, 55.058347
lon_min,lon_max=5.8663153, 15.0418962

lat_step=0.18
lon_step=0.27

latitudes=np.arange(lat_min, lat_max, lat_step)
longitudes=np.arange(lon_min, lon_max, lon_step)

i=0
lat_centers=[]
while i<len(latitudes)-1:
    lat=(latitudes[i]+latitudes[i+1])/2
    i+=1
    lat_centers.append(lat)

i=0
lon_centers=[]
while i<len(longitudes)-1:
    lon=(longitudes[i]+longitudes[i+1])/2
    i+=1
    lon_centers.append(lon)

center_points=[(lat, lon) for lat in lat_centers for lon in lon_centers]

def generate_prices(year):
    base_prices = {
        "apartment": {"min": 1500 + (year - 2010) * 100, "max": 3000 + (year - 2010) * 200},
        "villa": {"min": 2000 + (year - 2010) * 150, "max": 4000 + (year - 2010) * 250},
        "land": {"min": 800 + (year - 2010) * 80, "max": 1600 + (year - 2010) * 120},
    }
    return base_prices

data = []
for lat, lon in center_points:
    for year in range(2010, 2021):
        prices = generate_prices(year)
        row = {
            "latitude": lat,
            "longitude": lon,
            "year": year,
            "apartment_min": prices["apartment"]["min"],
            "apartment_max": prices["apartment"]["max"],
            "villa_min": prices["villa"]["min"],
            "villa_max": prices["villa"]["max"],
            "land_min": prices["land"]["min"],
            "land_max": prices["land"]["max"],
        }
        data.append(row)

with open('D:\\germany_real_estate_prices_final.csv', 'w', newline='') as csvfile:
    fieldnames = ["latitude", "longitude", "year", "apartment_min", "apartment_max", "villa_min", "villa_max", "land_min", "land_max"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in data:
        writer.writerow(row)
