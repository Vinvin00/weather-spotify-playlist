"""Map weather conditions to search keywords and genre tags."""


def weather_to_mood(weather: dict) -> dict:
    """
    Convert weather data into search keywords and genre preferences.

    Returns dict with:
        - keywords: list of search terms (2-3 mood words)
        - genres: list of genre tags that fit the weather
        - vibe: str — one-word summary like "upbeat", "melancholy", "cozy", "intense"
    """
    code = weather.get("weather_code", 0)
    temp = weather.get("temperature", 15)
    wind = weather.get("wind_speed", 0)
    is_day = weather.get("is_day", True)

    # Base mood from weather_code
    if code == 0 and is_day:
        keywords = ["happy", "upbeat", "sunshine", "feel good"]
        genres = ["pop", "indie pop", "summer", "dance pop", "tropical"]
        vibe = "upbeat"
    elif code == 0 and not is_day:
        keywords = ["chill night", "smooth", "evening", "late night"]
        genres = ["r-n-b", "neo soul", "jazz", "chill", "lo-fi"]
        vibe = "smooth"
    elif code in (1, 2, 3):
        keywords = ["indie", "dreamy", "mellow", "easy going"]
        genres = ["indie", "alternative", "dream pop", "indie folk", "soft rock"]
        vibe = "mellow"
    elif code in (45, 48):
        keywords = ["atmospheric", "ambient", "ethereal", "hazy"]
        genres = ["ambient", "shoegaze", "post-rock", "electronic", "downtempo"]
        vibe = "atmospheric"
    elif 51 <= code <= 55:
        keywords = ["gentle rain", "acoustic", "soft", "tender"]
        genres = ["acoustic", "singer-songwriter", "folk", "indie", "chill"]
        vibe = "tender"
    elif 61 <= code <= 65:
        keywords = ["rainy day", "melancholy", "reflective", "moody"]
        genres = ["indie", "alternative", "indie rock", "sad", "rainy-day"]
        vibe = "melancholy"
    elif 71 <= code <= 75:
        keywords = ["winter", "cozy", "warm", "peaceful"]
        genres = ["acoustic", "ambient", "folk", "piano", "classical"]
        vibe = "cozy"
    elif 80 <= code <= 82:
        keywords = ["energetic rain", "dramatic", "powerful"]
        genres = ["rock", "alternative", "post-rock", "indie rock"]
        vibe = "dramatic"
    elif code in (95, 96, 99):
        keywords = ["intense", "dark", "powerful", "electric"]
        genres = ["electronic", "industrial", "metal", "drum-and-bass"]
        vibe = "intense"
    else:
        keywords = ["indie", "mellow", "easy going"]
        genres = ["indie", "pop", "alternative"]
        vibe = "mellow"

    # Temperature modifiers
    if temp > 30:
        keywords = keywords + ["summer", "tropical"]
    elif temp < 5:
        keywords = keywords + ["winter", "cozy"]

    # Wind modifier
    if wind > 30:
        keywords = keywords + ["energetic"]

    return {
        "keywords": keywords,
        "genres": genres,
        "vibe": vibe,
    }
