import requests

city = input("Enter city name:").strip()

if not city:
    print("City name cannot be empty.")
    exit()

geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
geocoding_params = {
    "name": city,
    "count": 1,
    "language": "en",
    "format": "json",
}

try:
    response = requests.get(geocoding_url, params=geocoding_params, timeout=10)
    response.raise_for_status()
    location_data = response.json()
except requests.exceptions.RequestException:
    print("Could not find the city. Please check your internet connection and try again.")
    exit()
except ValueError:
    print("Could not read city data from the server.")
    exit()

try:
    location = location_data["results"][0]
    lat = location["latitude"]
    lon = location["longitude"]
    location_name = location["name"]
    country = location["country"]
except (KeyError, IndexError):
    print("City not found. Please try another city name.")
    exit()

weather_fields = [
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
]
current_weather = ",".join(weather_fields)
daily_weather = "temperature_2m_max,temperature_2m_min"
url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={lat}"
    f"&longitude={lon}"
    f"&current={current_weather}"
    f"&daily={daily_weather}"
    "&forecast_days=7"
    "&timezone=auto"
)

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

    daily = data["daily"]
    daily_units = data["daily_units"]
    forecast_dates = daily["time"]
    max_temperatures = daily["temperature_2m_max"]
    min_temperatures = daily["temperature_2m_min"]
    max_temperature_unit = daily_units["temperature_2m_max"]
    min_temperature_unit = daily_units["temperature_2m_min"]
except KeyError:
    print("Weather data is missing some information.")
    exit()

if not forecast_dates or not max_temperatures or not min_temperatures:
    print("Weather data is missing forecast information.")
    exit()

print("\nCurrent Weather Report")
print("----------------------")
print(f"Location      : {location_name}, {country}")
print(f"Coordinates   : {lat}, {lon}")
print(f"Temperature   : {temperature} {temperature_unit}")
print(f"Feels like    : {feels_like} {feels_like_unit}")
print(f"Humidity      : {humidity} {humidity_unit}")
print(f"Precipitation : {precipitation} {precipitation_unit}")
print(f"Wind speed    : {wind_speed} {wind_speed_unit}")

print("\nToday's Forecast")
print("----------------")
print(f"High          : {max_temperatures[0]} {max_temperature_unit}")
print(f"Low           : {min_temperatures[0]} {min_temperature_unit}")

print("\n7-Day Forecast")
print("--------------")
for index in range(min(len(forecast_dates), len(min_temperatures), len(max_temperatures))):
    print(
        f"{forecast_dates[index]} : "
        f"{min_temperatures[index]} {min_temperature_unit} - "
        f"{max_temperatures[index]} {max_temperature_unit}"
    )
