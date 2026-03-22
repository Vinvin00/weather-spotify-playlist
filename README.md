# Weather-Based Spotify Playlist Updater

Updates a Spotify playlist every hour based on the current weather in Madrid, Spain. Uses Open-Meteo for weather and Spotify's API via spotipy.

## How It Works

- Fetches weather from Open-Meteo (Madrid: 40.4168, -3.7038)
- Maps temperature and conditions to music moods
- Replaces playlist tracks with 5 new mood-appropriate songs

### Weather → Mood Mapping

| Conditions | Moods |
|------------|-------|
| Temp < 5°C | chill, lo-fi, ambient |
| 5–15°C | indie, alternative, acoustic |
| 15–25°C | pop, upbeat, feel-good |
| > 25°C | dance, funk, energetic |
| Rainy | jazz, lo-fi, ambient |
| Cloudy (>70%) | + melancholic |

## Setup

1. **Spotify Developer App**: Create an app at [developer.spotify.com](https://developer.spotify.com/dashboard) and note Client ID and Client Secret.

2. **Redirect URI**: Add `http://localhost:8080/callback` to your app's redirect URIs.

3. **Get Refresh Token**: Run locally once:
   ```bash
   pip install -r requirements.txt
   # Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env or as env vars
   python get_refresh_token.py
   ```
   Copy the printed refresh token for GitHub Secrets.

4. **GitHub Secrets**: Add these to your repo (Settings → Secrets and variables → Actions):
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
   - `SPOTIFY_REFRESH_TOKEN`
   - `PLAYLIST_ID` (from your playlist URL, e.g. `spotify.com/playlist/XXXX` → `XXXX`)

## Running

- **GitHub Actions**: Runs hourly (`0 * * * *`) or manually via workflow_dispatch
- **Local**: `python update_playlist.py` (requires .env with the four variables above)
