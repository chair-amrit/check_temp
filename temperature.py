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

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException:
    print("Could not fetch weather data. Please check your internet connection and try again.")
    exit()
except ValueError:
    print("Could not read weather data from the server.")
    exit()

try:
    temperature = data["current"]["temperature_2m"]
    unit = data["current_units"]["temperature_2m"]
except KeyError:
    print("Weather data is missing temperature information.")
    exit()

print(f"current temperature:{temperature} {unit}")
