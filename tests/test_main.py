import unittest

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

    def test_forecast_length_validation(self):
        data = {
            "daily": {
                "time": ["2026-07-27", "2026-07-28"],
                "temperature_2m_min": [24],
                "temperature_2m_max": [31, 32, 33],
            },
            "daily_units": {
                "temperature_2m_min": "deg C",
                "temperature_2m_max": "deg C",
            },
        }

        with self.assertRaises(ValueError):
            weather.get_forecast(data)

    def test_location_coordinate_type_validation(self):
        session = FakeSession(
            {
                "results": [
                    {
                        "name": "Bad City",
                        "country": "Nowhere",
                        "latitude": "bad",
                        "longitude": 80.2785,
                    }
                ]
            }
        )

        with self.assertRaises(ValueError):
            weather.get_location("Bad City", session)

    def test_get_location_uses_selected_location_index(self):
        session = FakeSession(
            {
                "results": [
                    {
                        "name": "Springfield",
                        "country": "United States",
                        "latitude": 39.7817,
                        "longitude": -89.6501,
                    },
                    {
                        "name": "Springfield",
                        "country": "United States",
                        "latitude": 44.0462,
                        "longitude": -123.022,
                    },
                ]
            }
        )

        location = weather.get_location("Springfield", session, location_index=2)

        self.assertEqual(location["latitude"], 44.0462)
        self.assertEqual(location["longitude"], -123.022)

    def test_choose_location_rejects_out_of_range_index(self):
        locations = [
            {
                "name": "Only City",
                "country": "Nowhere",
                "latitude": 1,
                "longitude": 2,
            }
        ]

        with self.assertRaises(ValueError):
            weather.choose_location(locations, 2)

    def test_current_weather_type_validation(self):
        data = {
            "current": {
                "temperature_2m": "hot",
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

        with self.assertRaises(ValueError):
            weather.get_current_weather(data)


if __name__ == "__main__":
    unittest.main()
