import requests

try:
    lat = float(input("Enter the latitude:"))
    lon = float(input("Enter the longitude:"))
except ValueError:
    print("Invalid input. Latitude and longitude must be numbers.")
    exit()

if not -90 <= lat <= 90:
    print("Invalid latitude. Latitude must be between -90 and 90.")
    exit()

if not -180 <= lon <= 180:
    print("Invalid longitude. Longitude must be between -180 and 180.")
    exit()

url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m"

response=requests.get(url)
data=response.json()

temperature=data["current"]["temperature_2m"]
unit=data["current_units"]["temperature_2m"]

print(f"current temperature:{temperature} {unit}")
