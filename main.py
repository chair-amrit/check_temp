import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Sequence, TypeVar, TypedDict

import requests


Number = int | float
T = TypeVar("T")
DEFAULT_REQUEST_TIMEOUT_SECONDS = 10
GEOCODING_RESULT_COUNT = 5

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


def require_string(value: Any, source: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{source} must be a string")

    return value


def format_location_choice(location: dict[str, Any]) -> str:
    name = require_string(location["name"], "location name")
    country = require_string(location["country"], "location country")
    parts = [name]

    admin1 = location.get("admin1")
    if isinstance(admin1, str) and admin1 not in parts:
        parts.append(admin1)

    if country not in parts:
        parts.append(country)

    return ", ".join(parts)


def get_location_candidates(results: list[Any]) -> list[dict[str, Any]]:
    locations: list[dict[str, Any]] = []

    for index, result in enumerate(results, start=1):
        if not isinstance(result, dict):
            raise ValueError(f"location {index} must be an object")

        require_fields(result, LOCATION_FIELDS, f"location {index}")
        locations.append(result)

    return locations


def choose_location(
    locations: list[dict[str, Any]], location_index: int = 1
) -> dict[str, Any]:
    if not 1 <= location_index <= len(locations):
        raise ValueError("location index must match one of the listed locations")

    return locations[location_index - 1]


def prompt_for_location_index(locations: list[dict[str, Any]]) -> int:
    print("Multiple matching cities found:", file=sys.stderr)
    for index, location in enumerate(locations, start=1):
        print(f"{index}. {format_location_choice(location)}", file=sys.stderr)

    while True:
        print("Select location number [1]: ", end="", file=sys.stderr)
        try:
            choice = input().strip()
        except EOFError:
            return 1

        if not choice:
            return 1

        try:
            selected_index = int(choice)
        except ValueError:
            print("Please enter a number from the list.", file=sys.stderr)
            continue

        if 1 <= selected_index <= len(locations):
            return selected_index

        print("Please choose one of the listed locations.", file=sys.stderr)


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
    session: requests.Session,
    url: str,
    params: dict[str, Any],
    timeout_seconds: Number,
) -> dict[str, Any]:
    response = session.get(url, params=params, timeout=timeout_seconds)
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


def get_location(
    city: str,
    session: requests.Session,
    timeout_seconds: Number = DEFAULT_REQUEST_TIMEOUT_SECONDS,
    location_index: int = 1,
) -> Location:
    locations = get_locations(city, session, timeout_seconds)
    return build_location(choose_location(locations, location_index))


def get_location_data(
    city: str,
    session: requests.Session,
    timeout_seconds: Number,
) -> dict[str, Any]:
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    geocoding_params = {
        "name": city,
        "count": GEOCODING_RESULT_COUNT,
        "language": "en",
        "format": "json",
    }

    location_data = fetch_json(
        session, geocoding_url, geocoding_params, timeout_seconds
    )
    return location_data


def get_locations(
    city: str,
    session: requests.Session,
    timeout_seconds: Number,
) -> list[dict[str, Any]]:
    location_data = get_location_data(city, session, timeout_seconds)

    results = location_data.get("results", [])
    if not isinstance(results, list):
        raise ValueError("location results must be a list")

    if not results:
        raise LookupError("city not found")

    return get_location_candidates(results)


def build_location(location: dict[str, Any]) -> Location:
    latitude = require_number(location["latitude"], "location latitude")
    longitude = require_number(location["longitude"], "location longitude")

    return {
        "name": require_string(location["name"], "location name"),
        "country": require_string(location["country"], "location country"),
        "latitude": latitude,
        "longitude": longitude,
    }


def get_weather_data(
    latitude: Number,
    longitude: Number,
    session: requests.Session,
    timeout_seconds: Number,
    temperature_unit: str,
    wind_speed_unit: str,
) -> dict[str, Any]:
    url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(CURRENT_WEATHER_FIELDS),
        "daily": ",".join(DAILY_WEATHER_FIELDS),
        "forecast_days": 7,
        "temperature_unit": temperature_unit,
        "wind_speed_unit": wind_speed_unit,
        "timezone": "auto",
    }

    return fetch_json(session, url, weather_params, timeout_seconds)


def positive_float(value: str) -> float:
    try:
        parsed_value = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a number") from error

    if parsed_value <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")

    return parsed_value


def positive_int(value: str) -> int:
    try:
        parsed_value = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error

    if parsed_value <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")

    return parsed_value


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
        "temperature_unit": require_string(
            units["temperature_2m"], "temperature unit"
        ),
        "feels_like": require_number(current["apparent_temperature"], "feels like"),
        "feels_like_unit": require_string(
            units["apparent_temperature"], "feels like unit"
        ),
        "humidity": require_number(current["relative_humidity_2m"], "humidity"),
        "humidity_unit": require_string(
            units["relative_humidity_2m"], "humidity unit"
        ),
        "precipitation": require_number(current["precipitation"], "precipitation"),
        "precipitation_unit": require_string(
            units["precipitation"], "precipitation unit"
        ),
        "wind_speed": require_number(current["wind_speed_10m"], "wind speed"),
        "wind_speed_unit": require_string(
            units["wind_speed_10m"], "wind speed unit"
        ),
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
        "max_temperature_unit": require_string(
            daily_units["temperature_2m_max"], "forecast maximum temperature unit"
        ),
        "min_temperature_unit": require_string(
            daily_units["temperature_2m_min"], "forecast minimum temperature unit"
        ),
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
        "--timeout",
        type=positive_float,
        default=DEFAULT_REQUEST_TIMEOUT_SECONDS,
        help=(
            "Request timeout in seconds. "
            f"Defaults to {DEFAULT_REQUEST_TIMEOUT_SECONDS}."
        ),
    )
    parser.add_argument(
        "--temperature-unit",
        choices=("celsius", "fahrenheit"),
        default="celsius",
        help="Temperature unit for the weather report. Defaults to celsius.",
    )
    parser.add_argument(
        "--wind-speed-unit",
        choices=("kmh", "mph"),
        default="kmh",
        help="Wind speed unit for the weather report. Defaults to kmh.",
    )
    parser.add_argument(
        "--location-index",
        type=positive_int,
        help=(
            "Select a 1-based location result without prompting. "
            "Defaults to an interactive prompt when multiple matches exist."
        ),
    )
    parser.add_argument(
        "city",
        nargs="*",
        help="City name to search for. If omitted, you will be prompted.",
    )
    return parser.parse_args(args)


def get_city_from_args(parsed_args: argparse.Namespace) -> str:
    if parsed_args.city:
        return " ".join(parsed_args.city).strip()

    return input("Enter city name:").strip()


def main(args: list[str] | None = None) -> int:
    parsed_args = parse_args(sys.argv[1:] if args is None else args)
    city = get_city_from_args(parsed_args)
    timeout_seconds = parsed_args.timeout
    temperature_unit = parsed_args.temperature_unit
    wind_speed_unit = parsed_args.wind_speed_unit
    location_index = parsed_args.location_index

    if not city:
        print("City name cannot be empty.", file=sys.stderr)
        return 1

    try:
        with requests.Session() as session:
            locations = run_service_call(
                lambda: get_locations(city, session, timeout_seconds),
                LOCATION_ERROR_MESSAGES,
            )
            selected_index = location_index
            if selected_index is None:
                selected_index = (
                    prompt_for_location_index(locations) if len(locations) > 1 else 1
                )

            location = build_location(choose_location(locations, selected_index))
            weather_data = run_service_call(
                lambda: get_weather_data(
                    location["latitude"],
                    location["longitude"],
                    session,
                    timeout_seconds,
                    temperature_unit,
                    wind_speed_unit,
                ),
                WEATHER_ERROR_MESSAGES,
            )
        report = build_weather_report(location, weather_data)
    except LookupError:
        print("City not found. Please try another city name.", file=sys.stderr)
        return 1
    except AppError as error:
        print(error.message, file=sys.stderr)
        return 1
    except (TypeError, ValueError):
        print(WEATHER_ERROR_MESSAGES.malformed, file=sys.stderr)
        return 1

    print_weather_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
