"""Update playlist tracks and metadata."""

from datetime import datetime, timezone

import spotipy

import config


def update_playlist(sp: spotipy.Spotify, track_uris: list, weather: dict) -> None:
    """
    Replace all tracks in the playlist and update the description.

    Steps:
    1. sp.playlist_replace_items(PLAYLIST_ID, track_uris)
    2. Build description with weather info and timestamp
    3. sp.playlist_change_details(PLAYLIST_ID, description=description)
    """
    sp.playlist_replace_items(config.PLAYLIST_ID, track_uris)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    desc = weather.get("description", "Unknown")
    temp = weather.get("temperature", "?")
    description = f"🌤️ Updated for Segovia weather: {desc}, {temp}°C | Last updated: {now}"

    sp.playlist_change_details(config.PLAYLIST_ID, description=description)
