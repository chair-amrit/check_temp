import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Sequence, TypeVar, TypedDict

import requests


Number = int | float
T = TypeVar("T")
REQUEST_TIMEOUT_SECONDS = 10

LOCATION_FIELDS = ("name", "country", "latitude", "longitude")
CURRENT_WEATHER_FIELDS = (
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
)
DAILY_FORECAST_FIELDS = ("time", "temperature_2m_max", "temperature_2m_min")
DAILY_WEATHER_FIELDS = ("temperature_2m_max", "temperature_2m_min")


class Location(TypedDict):
    name: str
    country: str
    latitude: Number
    longitude: Number


class CurrentWeather(TypedDict):
    temperature: Number
    temperature_unit: str
    feels_like: Number
    feels_like_unit: str
    humidity: Number
    humidity_unit: str
    precipitation: Number
    precipitation_unit: str
    wind_speed: Number
    wind_speed_unit: str


class Forecast(TypedDict):
    dates: list[str]
    max_temperatures: list[Number]
    min_temperatures: list[Number]
    max_temperature_unit: str
    min_temperature_unit: str


class WeatherReport(TypedDict):
    location: Location
    current_weather: CurrentWeather
    forecast: Forecast


@dataclass(frozen=True)
class ServiceErrorMessages:
    timeout: str
    connection: str
    http: str
    request: str
    malformed: str


class AppError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


LOCATION_ERROR_MESSAGES = ServiceErrorMessages(
    timeout="Location request timed out. Please try again.",
    connection=(
        "Could not connect to the location service. "
        "Please check your internet connection."
    ),
    http="Location service is unavailable. Please try again later.",
    request="Location request failed. Please try again.",
    malformed="Location service returned malformed data.",
)
WEATHER_ERROR_MESSAGES = ServiceErrorMessages(
    timeout="Weather request timed out. Please try again.",
    connection=(
        "Could not connect to the weather service. "
        "Please check your internet connection."
    ),
    http="Weather API is unavailable. Please try again later.",
    request="Weather request failed. Please try again.",
    malformed="Weather API returned malformed data.",
)


def require_fields(data: dict[str, Any], fields: Sequence[str], source: str) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{source} must be an object")

    missing_fields = [field for field in fields if field not in data]
    if missing_fields:
        raise ValueError(f"{source} missing fields: {', '.join(missing_fields)}")


def require_number(value: Any, source: str) -> Number:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{source} must be a number")

    return value


def require_number_list(value: Any, source: str) -> list[Number]:
    if not isinstance(value, list):
        raise ValueError(f"{source} must be a list")

    return [require_number(item, f"{source} item") for item in value]


def require_string_list(value: Any, source: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{source} must be a list")

    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"{source} items must be strings")

    return value


def fetch_json(
    session: requests.Session, url: str, params: dict[str, Any]
) -> dict[str, Any]:
    response = session.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("API response must be an object")

    return payload


def run_service_call(call: Callable[[], T], messages: ServiceErrorMessages) -> T:
    try:
        return call()
    except requests.exceptions.Timeout as error:
        raise AppError(messages.timeout) from error
    except requests.exceptions.ConnectionError as error:
        raise AppError(messages.connection) from error
    except requests.exceptions.HTTPError as error:
        raise AppError(messages.http) from error
    except requests.exceptions.RequestException as error:
        raise AppError(messages.request) from error
    except (TypeError, ValueError) as error:
        raise AppError(messages.malformed) from error


def get_location(city: str, session: requests.Session) -> Location:
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    geocoding_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    location_data = fetch_json(session, geocoding_url, geocoding_params)

    results = location_data.get("results", [])
    if not results:
        raise LookupError("city not found")

    location = results[0]
    require_fields(location, LOCATION_FIELDS, "location")
    latitude = require_number(location["latitude"], "location latitude")
    longitude = require_number(location["longitude"], "location longitude")

    return {
        "name": location["name"],
        "country": location["country"],
        "latitude": latitude,
        "longitude": longitude,
    }


def get_weather_data(
    latitude: Number, longitude: Number, session: requests.Session
) -> dict[str, Any]:
    url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(CURRENT_WEATHER_FIELDS),
        "daily": ",".join(DAILY_WEATHER_FIELDS),
        "forecast_days": 7,
        "timezone": "auto",
    }

    return fetch_json(session, url, weather_params)


def get_current_weather(data: dict[str, Any]) -> CurrentWeather:
    require_fields(data, ["current", "current_units"], "weather data")

    current = data["current"]
    units = data["current_units"]
    require_fields(
        current,
        CURRENT_WEATHER_FIELDS,
        "current weather",
    )
    require_fields(
        units,
        CURRENT_WEATHER_FIELDS,
        "current weather units",
    )

    return {
        "temperature": require_number(current["temperature_2m"], "temperature"),
        "temperature_unit": units["temperature_2m"],
        "feels_like": require_number(current["apparent_temperature"], "feels like"),
        "feels_like_unit": units["apparent_temperature"],
        "humidity": require_number(current["relative_humidity_2m"], "humidity"),
        "humidity_unit": units["relative_humidity_2m"],
        "precipitation": require_number(current["precipitation"], "precipitation"),
        "precipitation_unit": units["precipitation"],
        "wind_speed": require_number(current["wind_speed_10m"], "wind speed"),
        "wind_speed_unit": units["wind_speed_10m"],
    }


def get_forecast(data: dict[str, Any]) -> Forecast:
    require_fields(data, ["daily", "daily_units"], "weather data")

    daily = data["daily"]
    daily_units = data["daily_units"]
    require_fields(
        daily,
        DAILY_FORECAST_FIELDS,
        "daily forecast",
    )
    require_fields(
        daily_units,
        DAILY_WEATHER_FIELDS,
        "daily forecast units",
    )

    forecast: Forecast = {
        "dates": require_string_list(daily["time"], "forecast dates"),
        "max_temperatures": require_number_list(
            daily["temperature_2m_max"], "forecast maximum temperatures"
        ),
        "min_temperatures": require_number_list(
            daily["temperature_2m_min"], "forecast minimum temperatures"
        ),
        "max_temperature_unit": daily_units["temperature_2m_max"],
        "min_temperature_unit": daily_units["temperature_2m_min"],
    }

    if (
        not forecast["dates"]
        or not forecast["max_temperatures"]
        or not forecast["min_temperatures"]
    ):
        raise ValueError("missing forecast information")

    if not (
        len(forecast["dates"])
        == len(forecast["max_temperatures"])
        == len(forecast["min_temperatures"])
    ):
        raise ValueError("forecast arrays must have matching lengths")

    return forecast


def build_weather_report(
    location: Location, weather_data: dict[str, Any]
) -> WeatherReport:
    return {
        "location": location,
        "current_weather": get_current_weather(weather_data),
        "forecast": get_forecast(weather_data),
    }


def format_number(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.1f}"

    return str(value)


def print_weather_report(report: WeatherReport) -> None:
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
    for index, date in enumerate(forecast["dates"]):
        low = (
            f"{format_number(forecast['min_temperatures'][index])} "
            f"{forecast['min_temperature_unit']}"
        )
        high = (
            f"{format_number(forecast['max_temperatures'][index])} "
            f"{forecast['max_temperature_unit']}"
        )
        print(f"{date:<12} {low:>10} {high:>10}")


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch and print a weather report for a city."
    )
    parser.add_argument(
        "city",
        nargs="*",
        help="City name to search for. If omitted, you will be prompted.",
    )
    return parser.parse_args(args)


def get_city_from_args(args: list[str]) -> str:
    parsed_args = parse_args(args)
    if parsed_args.city:
        return " ".join(parsed_args.city).strip()

    return input("Enter city name:").strip()


def main(args: list[str] | None = None) -> int:
    city = get_city_from_args(sys.argv[1:] if args is None else args)

    if not city:
        print("City name cannot be empty.")
        return 1

    session = requests.Session()

    try:
        location = run_service_call(
            lambda: get_location(city, session), LOCATION_ERROR_MESSAGES
        )
        weather_data = run_service_call(
            lambda: get_weather_data(
                location["latitude"], location["longitude"], session
            ),
            WEATHER_ERROR_MESSAGES,
        )
        report = build_weather_report(location, weather_data)
    except LookupError:
        print("City not found. Please try another city name.")
        return 1
    except AppError as error:
        print(error.message)
        return 1
    except (TypeError, ValueError):
        print(WEATHER_ERROR_MESSAGES.malformed)
        return 1

    print_weather_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
