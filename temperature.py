import requests


def get_location(city):
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    geocoding_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    response = requests.get(geocoding_url, params=geocoding_params, timeout=10)
    response.raise_for_status()
    location_data = response.json()

    location = location_data["results"][0]
    return {
        "name": location["name"],
        "country": location["country"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
    }


def get_weather_data(lat, lon):
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

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_current_weather(data):
    current = data["current"]
    units = data["current_units"]

    return {
        "temperature": current["temperature_2m"],
        "temperature_unit": units["temperature_2m"],
        "feels_like": current["apparent_temperature"],
        "feels_like_unit": units["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "humidity_unit": units["relative_humidity_2m"],
        "precipitation": current["precipitation"],
        "precipitation_unit": units["precipitation"],
        "wind_speed": current["wind_speed_10m"],
        "wind_speed_unit": units["wind_speed_10m"],
    }


def get_forecast(data):
    daily = data["daily"]
    daily_units = data["daily_units"]

    forecast = {
        "dates": daily["time"],
        "max_temperatures": daily["temperature_2m_max"],
        "min_temperatures": daily["temperature_2m_min"],
        "max_temperature_unit": daily_units["temperature_2m_max"],
        "min_temperature_unit": daily_units["temperature_2m_min"],
    }

    if (
        not forecast["dates"]
        or not forecast["max_temperatures"]
        or not forecast["min_temperatures"]
    ):
        raise ValueError("missing forecast information")

    return forecast


def print_weather_report(location, current_weather, forecast):
    print("\nWeather Report")
    print("=" * 40)
    print(f"Location      : {location['name']}, {location['country']}")
    print(f"Coordinates   : {location['latitude']}, {location['longitude']}")
    print("-" * 40)
    print(f"Temperature   : {current_weather['temperature']} {current_weather['temperature_unit']}")
    print(f"Feels like    : {current_weather['feels_like']} {current_weather['feels_like_unit']}")
    print(f"Wind          : {current_weather['wind_speed']} {current_weather['wind_speed_unit']}")
    print(f"Humidity      : {current_weather['humidity']}{current_weather['humidity_unit']}")
    print(f"Precipitation : {current_weather['precipitation']} {current_weather['precipitation_unit']}")
    print("-" * 40)
    print(
        f"Today         : {forecast['min_temperatures'][0]} "
        f"{forecast['min_temperature_unit']} - "
        f"{forecast['max_temperatures'][0]} {forecast['max_temperature_unit']}"
    )

    print("\n7-Day Forecast")
    print("-" * 40)
    print(f"{'Date':<12} {'Low':>10} {'High':>10}")
    print("-" * 40)
    forecast_days = min(
        len(forecast["dates"]),
        len(forecast["min_temperatures"]),
        len(forecast["max_temperatures"]),
    )
    for index in range(forecast_days):
        low = f"{forecast['min_temperatures'][index]} {forecast['min_temperature_unit']}"
        high = f"{forecast['max_temperatures'][index]} {forecast['max_temperature_unit']}"
        print(f"{forecast['dates'][index]:<12} {low:>10} {high:>10}")


def main():
    city = input("Enter city name:").strip()

    if not city:
        print("City name cannot be empty.")
        return

    try:
        location = get_location(city)
    except requests.exceptions.RequestException:
        print("Could not find the city. Please check your internet connection and try again.")
        return
    except ValueError:
        print("Could not read city data from the server.")
        return
    except (KeyError, IndexError):
        print("City not found. Please try another city name.")
        return

    try:
        weather_data = get_weather_data(location["latitude"], location["longitude"])
    except requests.exceptions.RequestException:
        print("Could not fetch weather data. Please check your internet connection and try again.")
        return
    except ValueError:
        print("Could not read weather data from the server.")
        return

    try:
        current_weather = get_current_weather(weather_data)
        forecast = get_forecast(weather_data)
    except KeyError:
        print("Weather data is missing some information.")
        return
    except ValueError:
        print("Weather data is missing forecast information.")
        return

    print_weather_report(location, current_weather, forecast)


if __name__ == "__main__":
    main()
