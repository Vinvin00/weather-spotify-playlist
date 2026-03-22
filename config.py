"""Configuration constants. Secrets from environment (no defaults)."""

import os

# --- SECRETS (from environment / GitHub Secrets) ---
SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_REFRESH_TOKEN = os.environ.get("SPOTIFY_REFRESH_TOKEN")  # None when getting initial token

# --- NON-SECRET CONFIG ---
PLAYLIST_ID = os.environ.get("PLAYLIST_ID", "162eVgObhhCkttKtbYS5pp")

# Segovia, Spain coordinates (fixed — no geolocation needed)
LATITUDE = float(os.environ.get("LATITUDE", "40.9429"))
LONGITUDE = float(os.environ.get("LONGITUDE", "-4.1088"))

# Playlist settings
PLAYLIST_SIZE = 50  # Number of tracks in the final playlist
TOP_TRACKS_LIMIT = 500  # How many top tracks to analyze for taste profile

# Spotify API scopes needed
SCOPES = [
    "user-top-read",
    "playlist-modify-public",
    "playlist-modify-private",
    "ugc-image-upload",
]
