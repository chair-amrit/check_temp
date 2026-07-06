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

weather_fields = [
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
]
current_weather = ",".join(weather_fields)
url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current={current_weather}"

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
    current = data["current"]
    units = data["current_units"]

    temperature = current["temperature_2m"]
    temperature_unit = units["temperature_2m"]
    feels_like = current["apparent_temperature"]
    feels_like_unit = units["apparent_temperature"]
    humidity = current["relative_humidity_2m"]
    humidity_unit = units["relative_humidity_2m"]
    precipitation = current["precipitation"]
    precipitation_unit = units["precipitation"]
    wind_speed = current["wind_speed_10m"]
    wind_speed_unit = units["wind_speed_10m"]
except KeyError:
    print("Weather data is missing some information.")
    exit()

print("\nCurrent Weather Report")
print("----------------------")
print(f"Location      : {lat}, {lon}")
print(f"Temperature   : {temperature} {temperature_unit}")
print(f"Feels like    : {feels_like} {feels_like_unit}")
print(f"Humidity      : {humidity} {humidity_unit}")
print(f"Precipitation : {precipitation} {precipitation_unit}")
print(f"Wind speed    : {wind_speed} {wind_speed_unit}")
