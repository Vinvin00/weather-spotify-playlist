"""Map weather conditions to Spotify audio feature target ranges."""


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def weather_to_mood(weather: dict) -> dict:
    """
    Convert weather data into target audio feature ranges.

    Returns dict with keys for each audio feature, each containing:
        - target: float (ideal value)
        - min: float (acceptable minimum)
        - max: float (acceptable maximum)

    MAPPING LOGIC:
    Base mood from weather_code, then apply modifiers for temp/wind/night.
    Min/max: target ± 0.15 (tempo: ± 20, clamped to [60, 200])
    """
    code = weather.get("weather_code", 0)
    temp = weather.get("temperature", 15)
    wind = weather.get("wind_speed", 0)
    is_day = weather.get("is_day", True)

    # Base mood from weather_code
    if code == 0:
        base = {"energy": 0.7, "valence": 0.75, "danceability": 0.65, "tempo": 120, "acousticness": 0.3}
    elif code in (1, 2, 3):
        base = {"energy": 0.55, "valence": 0.6, "danceability": 0.55, "tempo": 110, "acousticness": 0.4}
    elif code in (45, 48):
        base = {"energy": 0.3, "valence": 0.4, "danceability": 0.35, "tempo": 85, "acousticness": 0.7}
    elif 51 <= code <= 55:
        base = {"energy": 0.35, "valence": 0.45, "danceability": 0.4, "tempo": 90, "acousticness": 0.65}
    elif 61 <= code <= 65:
        base = {"energy": 0.3, "valence": 0.35, "danceability": 0.35, "tempo": 85, "acousticness": 0.6}
    elif 71 <= code <= 75:
        base = {"energy": 0.25, "valence": 0.5, "danceability": 0.3, "tempo": 80, "acousticness": 0.7}
    elif code in (95, 96, 99):
        base = {"energy": 0.8, "valence": 0.3, "danceability": 0.5, "tempo": 130, "acousticness": 0.2}
    elif 80 <= code <= 82:
        base = {"energy": 0.4, "valence": 0.4, "danceability": 0.4, "tempo": 95, "acousticness": 0.55}
    else:
        base = {"energy": 0.5, "valence": 0.5, "danceability": 0.5, "tempo": 100, "acousticness": 0.5}

    # Modifiers
    if temp > 30:
        base["energy"] += 0.1
        base["valence"] += 0.05
    elif temp < 5:
        base["energy"] -= 0.1
        base["acousticness"] += 0.1
    if wind > 30:
        base["energy"] += 0.1
    if not is_day:
        base["energy"] -= 0.1
        base["valence"] -= 0.05
        base["acousticness"] += 0.1

    # Instrumentalness
    inst_target = 0.2 if not is_day else 0.1
    inst_max = 0.7 if not is_day else 0.5

    # Build result with min/max
    result = {}
    delta = 0.15
    tempo_delta = 20

    for key in ("energy", "valence", "danceability", "acousticness"):
        target = _clamp(base[key], 0, 1)
        result[key] = {
            "target": target,
            "min": _clamp(target - delta, 0, 1),
            "max": _clamp(target + delta, 0, 1),
        }

    result["tempo"] = {
        "target": base["tempo"],
        "min": _clamp(base["tempo"] - tempo_delta, 60, 200),
        "max": _clamp(base["tempo"] + tempo_delta, 60, 200),
    }

    result["instrumentalness"] = {
        "target": inst_target,
        "min": 0,
        "max": inst_max,
    }

    return result
