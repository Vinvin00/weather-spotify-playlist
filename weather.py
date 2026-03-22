"""Fetch and parse weather data from Open-Meteo API."""

from urllib.parse import urlencode

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather code to human-readable description
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather_description(code: int) -> str:
    """
    Convert WMO weather code to human-readable string.
    """
    return WEATHER_CODES.get(code, "Unknown")


def fetch_weather(lat: float, lon: float) -> dict:
    """
    Fetch current weather from Open-Meteo.

    Returns dict with keys:
        - temperature: float (°C)
        - apparent_temperature: float (°C) — "feels like"
        - humidity: float (%)
        - precipitation: float (mm)
        - rain: float (mm)
        - snowfall: float (cm)
        - weather_code: int (WMO code)
        - cloud_cover: float (%)
        - wind_speed: float (km/h)
        - is_day: bool (from Open-Meteo's is_day field)
        - description: str (human-readable weather, derived from weather_code)
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,snowfall,weather_code,cloud_cover,wind_speed_10m,is_day",
        "timezone": "auto",
    }
    url = f"{OPEN_METEO_URL}?{urlencode(params)}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    current = data.get("current", {})

    weather_code = int(current.get("weather_code", 0))
    is_day = current.get("is_day", 1) == 1

    return {
        "temperature": float(current.get("temperature_2m", 0)),
        "apparent_temperature": float(current.get("apparent_temperature", 0)),
        "humidity": float(current.get("relative_humidity_2m", 0)),
        "precipitation": float(current.get("precipitation", 0)),
        "rain": float(current.get("rain", 0)),
        "snowfall": float(current.get("snowfall", 0)),
        "weather_code": weather_code,
        "cloud_cover": float(current.get("cloud_cover", 0) or 0),
        "wind_speed": float(current.get("wind_speed_10m", 0)),
        "is_day": bool(is_day),
        "description": get_weather_description(weather_code),
    }
