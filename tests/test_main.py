import io
import unittest
from contextlib import redirect_stdout

import main as weather


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload

    def get(self, *args, **kwargs):
        return FakeResponse(self.payload)


class WeatherParsingTests(unittest.TestCase):
    def test_city_not_found(self):
        session = FakeSession({"results": []})

        with self.assertRaises(LookupError):
            weather.get_location("Missing City", session)

    def test_missing_api_fields(self):
        with self.assertRaises(ValueError):
            weather.get_current_weather({"current": {}})

    def test_successful_current_weather_parsing(self):
        data = {
            "current": {
                "temperature_2m": 27.4,
                "apparent_temperature": 29.1,
                "relative_humidity_2m": 72,
                "precipitation": 0,
                "wind_speed_10m": 8.5,
            },
            "current_units": {
                "temperature_2m": "deg C",
                "apparent_temperature": "deg C",
                "relative_humidity_2m": "%",
                "precipitation": "mm",
                "wind_speed_10m": "km/h",
            },
        }

        current_weather = weather.get_current_weather(data)

        self.assertEqual(current_weather["temperature"], 27.4)
        self.assertEqual(current_weather["temperature_unit"], "deg C")
        self.assertEqual(current_weather["feels_like"], 29.1)
        self.assertEqual(current_weather["humidity"], 72)
        self.assertEqual(current_weather["wind_speed"], 8.5)

    def test_forecast_length_handling(self):
        report = {
            "location": {
                "name": "Chennai",
                "country": "India",
                "latitude": 13.0878,
                "longitude": 80.2785,
            },
            "current_weather": {
                "temperature": 30,
                "temperature_unit": "deg C",
                "feels_like": 34,
                "feels_like_unit": "deg C",
                "humidity": 58,
                "humidity_unit": "%",
                "precipitation": 0,
                "precipitation_unit": "mm",
                "wind_speed": 12,
                "wind_speed_unit": "km/h",
            },
            "forecast": {
                "dates": ["2026-07-27", "2026-07-28"],
                "min_temperatures": [24],
                "max_temperatures": [31, 32, 33],
                "min_temperature_unit": "deg C",
                "max_temperature_unit": "deg C",
            },
        }
        output = io.StringIO()

        with redirect_stdout(output):
            weather.print_weather_report(report)

        report_text = output.getvalue()
        self.assertIn("2026-07-27", report_text)
        self.assertNotIn("2026-07-28", report_text)


if __name__ == "__main__":
    unittest.main()
