# Weather API Python Project

A simple Python command-line project created to understand the basics of working with APIs.

This project takes latitude and longitude as input, sends a request to the Open-Meteo Weather API, and displays the current weather information in a clean format.

I made this as a beginner-friendly B.Tech student project to practice:

- Taking user input in Python
- Validating input data
- Calling an external API
- Reading JSON responses
- Handling basic errors
- Displaying useful output in the terminal

## Features

- Accepts latitude and longitude from the user
- Validates latitude and longitude values
- Fetches live weather data using the Open-Meteo API
- Shows current weather details:
  - Temperature
  - Feels-like temperature
  - Humidity
  - Precipitation
  - Wind speed
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
Enter the latitude:13.08
Enter the longitude:80.27

Current Weather Report
----------------------
Location      : 13.08, 80.27
Temperature   : 31.4 °C
Feels like    : 35.2 °C
Humidity      : 70 %
Precipitation : 0.0 mm
Wind speed    : 10.5 km/h
```

## API Used

This project uses the free Open-Meteo API:

https://open-meteo.com/

No API key is required for basic usage.

## What I Learned

Through this project, I learned how a Python program can communicate with an external service using an API. I also understood how to work with JSON data, validate user input, and handle simple errors while building a real-world mini project.

## Future Improvements

Some possible improvements for this project are:

- Search weather by city name
- Show 7-day forecast
- Add command-line arguments
- Save weather reports to a file
- Convert this into a small Flask or FastAPI web API

## About

This is a basic learning project made as part of my programming practice as a B.Tech student.
