import sys
from typing import Any

import requests


def require_fields(data: dict[str, Any], fields: list[str], source: str) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{source} must be an object")

    missing_fields = [field for field in fields if field not in data]
    if missing_fields:
        raise ValueError(f"{source} missing fields: {', '.join(missing_fields)}")


def get_location(city: str, session: requests.Session) -> dict[str, Any]:
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    geocoding_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    response = session.get(geocoding_url, params=geocoding_params, timeout=10)
    response.raise_for_status()
    location_data = response.json()

    results = location_data.get("results", [])
    if not results:
        raise LookupError("city not found")

    location = results[0]
    require_fields(location, ["name", "country", "latitude", "longitude"], "location")

    return {
        "name": location["name"],
        "country": location["country"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
    }


def get_weather_data(
    latitude: float, longitude: float, session: requests.Session
) -> dict[str, Any]:
    weather_fields = [
        "temperature_2m",
        "apparent_temperature",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
    ]
    url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(weather_fields),
        "daily": "temperature_2m_max,temperature_2m_min",
        "forecast_days": 7,
        "timezone": "auto",
    }

    response = session.get(url, params=weather_params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_current_weather(data: dict[str, Any]) -> dict[str, Any]:
    require_fields(data, ["current", "current_units"], "weather data")

    current = data["current"]
    units = data["current_units"]
    require_fields(
        current,
        [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
        ],
        "current weather",
    )
    require_fields(
        units,
        [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
        ],
        "current weather units",
    )

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


def get_forecast(data: dict[str, Any]) -> dict[str, Any]:
    require_fields(data, ["daily", "daily_units"], "weather data")

    daily = data["daily"]
    daily_units = data["daily_units"]
    require_fields(
        daily,
        ["time", "temperature_2m_max", "temperature_2m_min"],
        "daily forecast",
    )
    require_fields(
        daily_units,
        ["temperature_2m_max", "temperature_2m_min"],
        "daily forecast units",
    )

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


def build_weather_report(
    location: dict[str, Any], weather_data: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    return {
        "location": location,
        "current_weather": get_current_weather(weather_data),
        "forecast": get_forecast(weather_data),
    }


def format_number(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.1f}"

    return str(value)


def print_weather_report(report: dict[str, dict[str, Any]]) -> None:
    location = report["location"]
    current_weather = report["current_weather"]
    forecast = report["forecast"]

    print("\nWeather Report")
    print("=" * 40)
    print(f"Location      : {location['name']}, {location['country']}")
    print(f"Coordinates   : {location['latitude']}, {location['longitude']}")
    print("-" * 40)
    print(
        f"Temperature   : {format_number(current_weather['temperature'])} "
        f"{current_weather['temperature_unit']}"
    )
    print(
        f"Feels like    : {format_number(current_weather['feels_like'])} "
        f"{current_weather['feels_like_unit']}"
    )
    print(
        f"Wind          : {format_number(current_weather['wind_speed'])} "
        f"{current_weather['wind_speed_unit']}"
    )
    print(f"Humidity      : {current_weather['humidity']}{current_weather['humidity_unit']}")
    print(
        f"Precipitation : {format_number(current_weather['precipitation'])} "
        f"{current_weather['precipitation_unit']}"
    )
    print("-" * 40)
    print(
        f"Today         : {format_number(forecast['min_temperatures'][0])} "
        f"{forecast['min_temperature_unit']} - "
        f"{format_number(forecast['max_temperatures'][0])} "
        f"{forecast['max_temperature_unit']}"
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
        low = (
            f"{format_number(forecast['min_temperatures'][index])} "
            f"{forecast['min_temperature_unit']}"
        )
        high = (
            f"{format_number(forecast['max_temperatures'][index])} "
            f"{forecast['max_temperature_unit']}"
        )
        print(f"{forecast['dates'][index]:<12} {low:>10} {high:>10}")


def get_city_from_args(args: list[str]) -> str:
    if args:
        return " ".join(args).strip()

    return input("Enter city name:").strip()


def main() -> None:
    city = get_city_from_args(sys.argv[1:])

    if not city:
        print("City name cannot be empty.")
        return

    session = requests.Session()

    try:
        location = get_location(city, session)
    except requests.exceptions.Timeout:
        print("Location request timed out. Please try again.")
        return
    except requests.exceptions.ConnectionError:
        print(
            "Could not connect to the location service. "
            "Please check your internet connection."
        )
        return
    except requests.exceptions.HTTPError:
        print("Location service is unavailable. Please try again later.")
        return
    except requests.exceptions.RequestException:
        print("Location request failed. Please try again.")
        return
    except LookupError:
        print("City not found. Please try another city name.")
        return
    except (TypeError, ValueError):
        print("Location service returned malformed data.")
        return

    try:
        weather_data = get_weather_data(
            location["latitude"], location["longitude"], session
        )
    except requests.exceptions.Timeout:
        print("Weather request timed out. Please try again.")
        return
    except requests.exceptions.ConnectionError:
        print(
            "Could not connect to the weather service. "
            "Please check your internet connection."
        )
        return
    except requests.exceptions.HTTPError:
        print("Weather API is unavailable. Please try again later.")
        return
    except requests.exceptions.RequestException:
        print("Weather request failed. Please try again.")
        return
    except ValueError:
        print("Weather API returned malformed data.")
        return

    try:
        report = build_weather_report(location, weather_data)
    except (TypeError, ValueError):
        print("Weather API returned malformed data.")
        return

    print_weather_report(report)


if __name__ == "__main__":
    main()
