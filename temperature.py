import requests

lat=input("Enter the latitude:")
lon=input("Enter the longitude:")

url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m"

response=requests.get(url)
data=response.json()

temperature=data["current"]["temperature_2m"]
unit=data["current_units"]["temperature_2m"]

print(f"current temperature:{temperature} {unit}")