# Weather API Python Project

A simple Python command-line project created to understand the basics of working with APIs.

This project takes a city name as input, finds its coordinates using geocoding, sends a request to the Open-Meteo Weather API, and displays the current weather information in a clean format.

I made this as a beginner-friendly B.Tech student project to practice:

- Taking user input in Python
- Validating input data
- Calling an external API
- Using geocoding to convert a city name into coordinates
- Reading JSON responses
- Handling basic errors
- Displaying useful output in the terminal

## Features

- Accepts a city name from the user
- Finds the latitude and longitude for the city
- Fetches live weather data using the Open-Meteo API
- Shows current weather details:
  - Temperature
  - Feels-like temperature
  - Humidity
  - Precipitation
  - Wind speed
- Shows today's high and low temperature
- Shows a 7-day temperature forecast
- Handles common errors like invalid input, network issues, and missing API data

## Technologies Used

- Python
- Requests library
- Open-Meteo Weather API

## How to Run

1. Clone this repository:

```bash
git clone https://github.com/your-username/weatherapi.git
```

2. Go inside the project folder:

```bash
cd weatherapi
```

3. Install the required package:

```bash
pip install requests
```

4. Run the Python file:

```bash
python temperature.py
```

If `python` does not work on Windows, try:

```bash
py temperature.py
```

## Example

```text
Enter city name:Chennai

Current Weather Report
----------------------
Location      : Chennai, India
Coordinates   : 13.0878, 80.2785
Temperature   : 31.4 deg C
Feels like    : 35.2 deg C
Humidity      : 70 %
Precipitation : 0.0 mm
Wind speed    : 10.5 km/h

Today's Forecast
----------------
High          : 33.1 deg C
Low           : 27.4 deg C

7-Day Forecast
--------------
2026-07-08 : 27.4 deg C - 33.1 deg C
2026-07-09 : 27.0 deg C - 32.8 deg C
2026-07-10 : 26.8 deg C - 32.5 deg C
```

## API Used

This project uses the free Open-Meteo Forecast API and Geocoding API:

https://open-meteo.com/

No API key is required for basic usage.

## What I Learned

Through this project, I learned how a Python program can communicate with external services using APIs. I also understood how to work with JSON data, convert city names into coordinates, validate user input, and handle simple errors while building a real-world mini project.

## Future Improvements

Some possible improvements for this project are:

- Add command-line arguments
- Save weather reports to a file
- Convert this into a small Flask or FastAPI web API

## About

This is a basic learning project made as part of my programming practice as a B.Tech student.
