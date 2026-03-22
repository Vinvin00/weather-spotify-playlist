"""
main.py — Entry point for weather-based Spotify playlist updater.

Flow:
1. Authenticate with Spotify
2. Fetch current weather for configured location
3. Map weather to mood (audio feature targets)
4. Build user's taste profile from their top tracks
5. Blend mood + taste into recommendation targets
6. Get current playlist track IDs (to avoid repeating)
7. Fetch and filter recommendations
8. Replace playlist contents
9. Generate and upload cover image
10. Log summary

Error handling:
- Wrap entire flow in try/except
- Log errors with full traceback
- Exit with code 1 on failure (so GitHub Actions marks the run as failed)
- Use Python's logging module, level=INFO
"""

import logging
import sys

from auth import get_spotify_client
from config import FRESHNESS_RATIO, LATITUDE, LONGITUDE, PLAYLIST_ID
from cover import generate_cover, upload_cover
from mood import weather_to_mood
from playlist import update_playlist
from recommend import blend_targets, get_recommendations
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

        # Step 3: Mood
        mood = weather_to_mood(weather)
        logger.info(
            f"Mood targets: energy={mood['energy']['target']:.2f}, valence={mood['valence']['target']:.2f}"
        )

        # Step 4: Taste
        logger.info("Building taste profile...")
        taste = build_taste_profile(sp)

        # Step 5: Blend
        blended = blend_targets(mood, taste, ratio=FRESHNESS_RATIO)

        # Step 6: Current playlist
        current = sp.playlist_items(PLAYLIST_ID, fields="items(track(id))")
        current_ids = set()
        for item in current.get("items", []):
            track = item.get("track") if item else None
            if track and track.get("id"):
                current_ids.add(track["id"])

        # Step 7: Recommend
        logger.info("Fetching recommendations...")
        track_uris = get_recommendations(sp, blended, taste, current_ids)
        logger.info(f"Selected {len(track_uris)} tracks")

        # Step 8: Update playlist
        update_playlist(sp, track_uris, weather)
        logger.info("✓ Playlist updated")

        # Step 9: Cover image (don't crash if it fails)
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
