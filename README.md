# Weather API Python Project

A simple Python command-line project made to understand the basics of working with APIs.

This project takes a city name as input, finds its latitude and longitude using geocoding, fetches live weather data from Open-Meteo, and prints a clean weather report in the terminal.

I made this as a beginner-friendly B.Tech student project to practice Python, API requests, JSON data, and basic error handling.

## Features

- Search weather by city name
- Convert city name into latitude and longitude
- Fetch current weather data
- Show temperature, feels-like temperature, wind speed, humidity, and precipitation
- Show today's high and low temperature
- Show a 7-day temperature forecast
- Handle invalid input, missing city data, API errors, and network issues
- Code is organized into reusable functions

## Technologies Used

- Python
- Requests library
- Open-Meteo Forecast API
- Open-Meteo Geocoding API

## Project Files

```text
weatherapi/
├── temperature.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone this repository:

```bash
git clone https://github.com/chair-amrit/check_temp.git
```

2. Go inside the project folder:

```bash
cd check_temp
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## How to Run

```bash
python temperature.py
```

On Windows, if `python` does not work, try:

```bash
py temperature.py
```

## Example Output

```text
Enter city name:Chennai

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
2026-07-08      30.5 deg C  38.6 deg C
2026-07-09      29.1 deg C  37.7 deg C
2026-07-10      28.4 deg C  37.8 deg C
```

## How It Works

1. The user enters a city name.
2. The program uses the Open-Meteo Geocoding API to get latitude and longitude.
3. The program sends those coordinates to the Open-Meteo Forecast API.
4. The API response is received as JSON.
5. The program extracts useful weather details and prints them in a readable format.

## Main Functions

- `get_location(city)` gets city details and coordinates
- `get_weather_data(lat, lon)` fetches weather data from the API
- `get_current_weather(data)` extracts current weather details
- `get_forecast(data)` extracts forecast details
- `print_weather_report(...)` prints the final report
- `main()` controls the program flow

## What I Learned

Through this project, I learned how Python can communicate with external APIs. I also practiced taking user input, validating data, handling errors, reading JSON responses, and organizing code into reusable functions.

## Future Improvements

- Add command-line arguments
- Save weather reports to a file
- Add hourly forecast
- Convert this into a small Flask or FastAPI web API

## About

This is a basic learning project made as part of my programming practice as a B.Tech student.
