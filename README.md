# Weather API CLI

A Python command-line weather application that searches for a city, resolves its
coordinates, fetches live forecast data from Open-Meteo, and prints a readable
weather report in the terminal.

The project is designed as a clean beginner-friendly API integration example,
with reusable functions, explicit error handling, typed function signatures, and
basic automated tests.

## Features

- Search weather by city name
- Resolve city name to latitude and longitude using Open-Meteo Geocoding API
- Fetch current weather from Open-Meteo Forecast API
- Display temperature, feels-like temperature, humidity, precipitation, and wind
  speed
- Display today's low and high temperature
- Display a 7-day temperature forecast
- Support both interactive input and command-line arguments
- Format numeric weather values consistently to one decimal place
- Handle empty input, city-not-found results, timeouts, network failures, API
  failures, and malformed API responses
- Keep API parsing, report building, and terminal printing separated
- Include unit tests for core parsing and edge cases

## Technologies

- Python 3
- Requests
- Open-Meteo Geocoding API
- Open-Meteo Forecast API
- unittest

## Project Structure

```text
weatherapi/
|-- main.py
|-- requirements.txt
|-- README.md
|-- tests/
|   `-- test_main.py
`-- .gitignore
```

## Installation

Clone the repository:

```bash
git clone https://github.com/chair-amrit/check_temp.git
cd check_temp
```

Install dependencies:

```bash
pip install -r requirements.txt
```

On Windows, if `python` does not work, use `py` instead.

## Usage

Run interactively:

```bash
python main.py
```

Then enter a city name when prompted:

```text
Enter city name: Chennai
```

Run with a command-line city argument:

```bash
python main.py London
```

For city names with multiple words:

```bash
python main.py New York
```

Windows alternative:

```bash
py main.py London
```

## Example Output

```text
Weather Report
========================================
Location      : Chennai, India
Coordinates   : 13.08784, 80.27847
----------------------------------------
Temperature   : 32.1 deg C
Feels like    : 35.7 deg C
Wind          : 12.1 km/h
Humidity      : 58%
Precipitation : 0.0 mm
----------------------------------------
Today         : 30.5 deg C - 38.6 deg C

7-Day Forecast
----------------------------------------
Date                Low       High
----------------------------------------
2026-07-27      30.5 deg C  38.6 deg C
2026-07-28      29.1 deg C  37.7 deg C
2026-07-29      28.4 deg C  37.8 deg C
```

## How It Works

1. The application accepts a city name from command-line arguments or interactive
   input.
2. `get_location()` calls the Open-Meteo Geocoding API and extracts the city
   name, country, latitude, and longitude.
3. `get_weather_data()` calls the Open-Meteo Forecast API using those
   coordinates.
4. `get_current_weather()` validates and extracts current weather fields.
5. `get_forecast()` validates and extracts daily forecast fields.
6. `build_weather_report()` combines location, current weather, and forecast
   data into a reusable report dictionary.
7. `print_weather_report()` formats and prints the final terminal output.

## Error Handling

The application gives clear messages for common failure cases:

- Empty city input
- City not found
- Location request timeout
- Weather request timeout
- Network connection failure
- API service unavailable
- Malformed or incomplete API response data

Required API fields are validated inside the parsing functions, so malformed
responses are detected close to where the data is used.

## Testing

Run the test suite:

```bash
python -m unittest discover -s tests
```

Windows alternative:

```bash
py -m unittest discover -s tests
```

The current tests cover:

- City not found
- Missing API fields
- Successful current weather parsing
- Forecast length handling when daily arrays have different lengths

## Main Functions

- `get_location(city, session)` resolves a city to location details.
- `get_weather_data(latitude, longitude, session)` fetches forecast data.
- `get_current_weather(data)` validates and extracts current weather.
- `get_forecast(data)` validates and extracts daily forecast data.
- `build_weather_report(location, weather_data)` builds reusable report data.
- `print_weather_report(report)` prints the terminal report.
- `get_city_from_args(args)` supports command-line city input.
- `main()` controls the application flow.

## Future Improvements

- Save weather reports to a file
- Add hourly forecast details
- Add unit conversion options
- Add JSON output mode for scripting
- Convert the project into a small Flask or FastAPI web API

## Author

Made by Amrit Rajkumar as a Python API practice project.
