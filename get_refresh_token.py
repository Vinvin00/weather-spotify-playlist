#!/usr/bin/env python3
"""
One-time script to obtain Spotify refresh token for use in GitHub Actions.
Run this locally: python get_refresh_token.py

You will be prompted to open a URL in your browser, log in to Spotify, and paste the redirect URL back.
The script will then print your refresh token to add to GitHub Secrets.
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private"

def main():
    client_id = os.environ.get("SPOTIFY_CLIENT_ID") or input("SPOTIFY_CLIENT_ID: ").strip()
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET") or input("SPOTIFY_CLIENT_SECRET: ").strip()

    if not client_id or not client_secret:
        print("Error: Client ID and Client Secret are required.")
        return

    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8080/callback",
        scope=SCOPE,
        cache_path=".cache",
        show_dialog=True,
    )

    print("\n1. Add this Redirect URI to your Spotify app: http://localhost:8080/callback")
    print("   (Spotify Dashboard → Your App → Edit Settings → Redirect URIs)\n")
    print("2. Opening browser for Spotify authorization...\n")

    token_info = sp_oauth.get_access_token()
    if token_info and token_info.get("refresh_token"):
        print("=" * 60)
        print("SUCCESS! Your refresh token:")
        print("=" * 60)
        print(token_info["refresh_token"])
        print("=" * 60)
        print("\nAdd this as SPOTIFY_REFRESH_TOKEN in your GitHub Secrets.")
        print("You can delete the .cache file after copying the token.")
    else:
        print("Failed to obtain refresh token. Try again.")


if __name__ == "__main__":
    main()
