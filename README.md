# Weather-Based Spotify Playlist Automation

Updates a Spotify playlist every hour via GitHub Actions. Fetches the current weather for Segovia, Spain; maps conditions to audio characteristics; blends with your personal taste profile; fetches recommendations; and replaces playlist contents. Also generates and uploads a dynamic cover image reflecting the weather.

**Stack**: Python 3.11+, spotipy, requests, Pillow. No database, server, or frontend — just a cron job.

## File Structure

```
weather-spotify-playlist/
├── main.py              # Entry point — orchestrates the pipeline
├── config.py            # Configuration constants
├── auth.py              # Spotify authentication (token refresh)
├── weather.py           # Fetch + parse weather data (Open-Meteo)
├── mood.py              # Map weather → audio feature targets
├── taste.py             # Build user's taste profile from top tracks
├── recommend.py         # Get + filter Spotify recommendations
├── playlist.py          # Update playlist tracks + metadata
├── cover.py             # Generate + upload dynamic cover image
├── requirements.txt
├── .github/workflows/update-playlist.yml
├── .gitignore
└── README.md
```

## How It Works

1. **Weather** → Open-Meteo API (free, no key)
2. **Mood** → Maps weather (clear, rain, snow, etc.) to Spotify audio features (energy, valence, danceability, tempo, acousticness)
3. **Taste** → Analyzes your top 50 tracks for personal preferences
4. **Blend** → 70% weather mood + 30% personal taste
5. **Recommend** → Spotify Recommendations API with blended targets + seeds from your taste
6. **Update** → Replaces playlist with 25 tracks + new description + dynamic cover image

## Setup

### 1. Spotify Developer App

Create an app at [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard). Add `http://localhost:8888/callback` to Redirect URIs.

### 2. Get Refresh Token

Run locally (one time):

```bash
pip install -r requirements.txt
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
python -c "from auth import get_initial_refresh_token; get_initial_refresh_token()"
```

Copy the printed refresh token for GitHub Secrets.

### 3. GitHub Secrets

Add these at `https://github.com/<username>/<repo>/settings/secrets/actions`:

| Secret | Description |
|--------|-------------|
| `SPOTIFY_CLIENT_ID` | From Spotify Developer Dashboard |
| `SPOTIFY_CLIENT_SECRET` | From Spotify Developer Dashboard |
| `SPOTIFY_REFRESH_TOKEN` | From step 2 |
| `PLAYLIST_ID` | From playlist URL: `spotify.com/playlist/XXXX` → `XXXX` |

### 4. Optional: Location

Default is Segovia, Spain (40.9429, -4.1088). Override via `LATITUDE` and `LONGITUDE` in the workflow env or secrets.

## Test Locally

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
export SPOTIFY_CLIENT_ID="..."
export SPOTIFY_CLIENT_SECRET="..."
export SPOTIFY_REFRESH_TOKEN="..."
export PLAYLIST_ID="162eVgObhhCkttKtbYS5pp"
python main.py
```

## Schedule

- **Cron**: Every hour (`0 * * * *`)
- **Manual**: Actions → Update Weather Playlist → Run workflow
