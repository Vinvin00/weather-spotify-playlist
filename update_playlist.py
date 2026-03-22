#!/usr/bin/env python3
"""
Weather-based Spotify playlist updater.
Fetches weather for Madrid and updates a Spotify playlist with mood-appropriate tracks.
"""

import json
import logging
import os
import random
import tempfile
from urllib.parse import urlencode

import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Madrid coordinates
MADRID_LAT = 40.4168
MADRID_LON = -3.7038
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def fetch_weather() -> dict:
    """Fetch current weather from Open-Meteo API for Madrid."""
    params = {
        "latitude": MADRID_LAT,
        "longitude": MADRID_LON,
        "current": ["temperature_2m", "precipitation", "cloud_cover"],
    }
    url = f"{OPEN_METEO_URL}?{urlencode(params)}"
    logger.info("Fetching weather from Open-Meteo API...")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    logger.info("Weather data received successfully")
    return data


def determine_mood(weather_data: dict) -> list[str]:
    """
    Determine music mood based on temperature and weather conditions.
    Returns a list of search keywords.
    """
    current = weather_data.get("current", {})
    temp = current.get("temperature_2m", 15)
    precipitation = current.get("precipitation", 0)
    cloud_cover = current.get("cloud_cover", 0)

    moods = []

    # Precipitation overrides temperature for chill vibes
    if precipitation and precipitation > 0:
        moods.extend(["jazz", "lo-fi", "ambient"])
        logger.info(f"Rainy conditions ({precipitation}mm) → adding jazz, lo-fi, ambient")
        return moods

    # Temperature-based mood
    if temp < 5:
        moods.extend(["chill", "lo-fi", "ambient"])
        logger.info(f"Cold ({temp}°C) → chill, lo-fi, ambient")
    elif temp < 15:
        moods.extend(["indie", "alternative", "acoustic"])
        logger.info(f"Cool ({temp}°C) → indie, alternative, acoustic")
    elif temp < 25:
        moods.extend(["pop", "upbeat", "feel-good"])
        logger.info(f"Warm ({temp}°C) → pop, upbeat, feel-good")
    else:
        moods.extend(["dance", "funk", "energetic"])
        logger.info(f"Hot ({temp}°C) → dance, funk, energetic")

    # Add melancholic if very cloudy
    if cloud_cover is not None and cloud_cover > 70:
        moods.append("melancholic")
        logger.info(f"Cloudy ({cloud_cover}%) → adding melancholic")

    return moods


def get_spotify_client():
    """Create Spotify client using OAuth with refresh token from environment."""
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    refresh_token = os.environ.get("SPOTIFY_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError(
            "Missing required env vars: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REFRESH_TOKEN"
        )

    # Create temp token cache for CI (SpotifyOAuth needs cache_path with refresh_token)
    token_data = {"refresh_token": refresh_token}
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(token_data, f)
        cache_path = f.name

    try:
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8080/callback",
            scope="playlist-modify-public playlist-modify-private playlist-read-private",
            cache_path=cache_path,
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp
    finally:
        try:
            os.unlink(cache_path)
        except OSError:
            pass


def search_tracks(sp: spotipy.Spotify, mood_keywords: list[str], limit: int = 5) -> list[str]:
    """Search Spotify for tracks matching mood keywords. Returns up to `limit` track URIs."""
    all_tracks = set()
    for keyword in mood_keywords:
        try:
            result = sp.search(q=keyword, type="track", limit=20)
            for item in result.get("tracks", {}).get("items", []):
                if item.get("uri"):
                    all_tracks.add(item["uri"])
        except Exception as e:
            logger.warning("Search failed for '%s': %s", keyword, e)

    if not all_tracks:
        logger.warning("No tracks found, falling back to general search")
        result = sp.search(q="chill", type="track", limit=20)
        for item in result.get("tracks", {}).get("items", []):
            if item.get("uri"):
                all_tracks.add(item["uri"])

    tracks_list = list(all_tracks)
    random.shuffle(tracks_list)
    return tracks_list[:limit]


def update_playlist(sp: spotipy.Spotify, playlist_id: str, track_uris: list[str]) -> None:
    """Remove all tracks from playlist and add new ones."""
    # Get current tracks
    try:
        playlist = sp.playlist(playlist_id)
        total = playlist.get("tracks", {}).get("total", 0)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch playlist: {e}") from e

    if total > 0:
        # Collect all track URIs to remove (Spotify API limit: 100 per request)
        track_refs = []
        offset = 0
        while offset < total:
            result = sp.playlist_items(playlist_id, offset=offset, fields="items(track(uri))")
            for item in result.get("items", []):
                uri = item.get("track", {}).get("uri")
                if uri:
                    track_refs.append({"uri": uri})
            offset += 100
            if len(result.get("items", [])) < 100:
                break

        # Remove in batches of 100
        for i in range(0, len(track_refs), 100):
            batch = track_refs[i : i + 100]
            sp.playlist_remove_all_occurrences_of_items(playlist_id, [t["uri"] for t in batch])
        logger.info("Removed %d tracks from playlist", len(track_refs))

    if track_uris:
        sp.playlist_add_items(playlist_id, track_uris)
        logger.info("Added %d new tracks to playlist", len(track_uris))


def main() -> None:
    """Main entry point."""
    print("=" * 60)
    print("Weather-Based Spotify Playlist Updater")
    print("=" * 60)

    try:
        # 1. Fetch weather
        weather_data = fetch_weather()
        current = weather_data.get("current", {})
        temp = current.get("temperature_2m", "N/A")
        precip = current.get("precipitation", "N/A")
        clouds = current.get("cloud_cover", "N/A")
        print(f"Weather (Madrid): temp={temp}°C, precipitation={precip}mm, clouds={clouds}%")

        # 2. Determine mood
        moods = determine_mood(weather_data)
        print(f"Selected moods: {moods}")

        # 3. Authenticate with Spotify
        print("Authenticating with Spotify...")
        sp = get_spotify_client()
        print("Spotify authentication successful")

        # 4. Search for tracks
        print("Searching for tracks...")
        track_uris = search_tracks(sp, moods, limit=5)
        if not track_uris:
            raise RuntimeError("No tracks found")
        print(f"Found {len(track_uris)} tracks to add")

        # 5. Update playlist
        playlist_id = os.environ.get("PLAYLIST_ID")
        if not playlist_id:
            raise ValueError("PLAYLIST_ID environment variable is required")

        print("Updating playlist...")
        update_playlist(sp, playlist_id, track_uris)

        print("=" * 60)
        print("SUCCESS: Playlist updated successfully!")
        print("=" * 60)

    except requests.RequestException as e:
        logger.error("Weather API error: %s", e)
        print(f"ERROR: Failed to fetch weather: {e}")
        raise
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        print(f"ERROR: {e}")
        raise
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
