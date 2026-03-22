"""
main.py — Entry point for weather-based Spotify playlist updater.

Flow:
1. Authenticate with Spotify
2. Fetch current weather for configured location
3. Map weather to mood (keywords/genres)
4. Build user's taste profile (top artists, genres — NO audio features)
5. Get current playlist tracks (to avoid repeats)
6. Search-based recommendations blending mood + taste
7. Replace playlist contents
8. Generate and upload cover image

Error handling:
- Wrap entire flow in try/except
- Log errors with full traceback
- Exit with code 1 on failure (so GitHub Actions marks the run as failed)
- Use Python's logging module, level=INFO
"""

import logging
import sys

from auth import get_spotify_client
from config import LATITUDE, LONGITUDE, PLAYLIST_ID
from cover import generate_cover, upload_cover
from mood import weather_to_mood
from playlist import update_playlist
from recommend import get_recommendations
from taste import build_taste_profile
from weather import fetch_weather

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    try:
        # Step 1: Auth
        logger.info("Authenticating with Spotify...")
        sp = get_spotify_client()

        # Step 2: Weather
        logger.info("Fetching weather...")
        weather = fetch_weather(LATITUDE, LONGITUDE)
        logger.info(f"Weather: {weather['description']}, {weather['temperature']}°C")

        # Step 3: Weather → mood keywords/genres
        mood = weather_to_mood(weather)
        logger.info(f"Mood: vibe={mood['vibe']}, keywords={mood['keywords'][:3]}")

        # Step 4: User's taste profile (top artists, genres — NO audio features)
        logger.info("Building taste profile...")
        taste = build_taste_profile(sp)

        # Step 5: Get current playlist tracks (to avoid repeats)
        current = sp.playlist_items(PLAYLIST_ID, fields="items(track(id))")
        current_ids = set()
        for item in current.get("items", []):
            track = item.get("track") if item else None
            if track and track.get("id"):
                current_ids.add(track["id"])

        # Step 6: Search-based recommendations blending mood + taste
        logger.info("Fetching recommendations...")
        track_uris = get_recommendations(sp, mood, taste, current_ids)
        logger.info(f"Selected {len(track_uris)} tracks")

        # Step 7: Update playlist
        update_playlist(sp, track_uris, weather)
        logger.info("✓ Playlist updated")

        # Step 8: Cover image (don't crash if it fails)
        try:
            logger.info("Generating cover image...")
            cover_b64 = generate_cover(weather)
            upload_cover(sp, cover_b64)
            logger.info("✓ Cover image uploaded")
        except Exception as e:
            logger.warning("Cover image upload failed (playlist updated successfully): %s", e)

        logger.info(
            f"✓ Done! Updated playlist with {len(track_uris)} tracks for "
            f"{weather['description']}, {weather['temperature']}°C"
        )

    except Exception as e:
        logger.error("Failed: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
