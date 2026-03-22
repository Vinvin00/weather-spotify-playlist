"""Spotify authentication — refresh token flow for headless CI."""

import json
import os
import tempfile

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import config


def get_spotify_client() -> spotipy.Spotify:
    """
    Create and return an authenticated Spotify client.
    Uses SpotifyOAuth with the refresh token from config.
    """
    if not config.SPOTIFY_REFRESH_TOKEN:
        raise ValueError("SPOTIFY_REFRESH_TOKEN is required. Run get_initial_refresh_token() first.")
    token_data = {"refresh_token": config.SPOTIFY_REFRESH_TOKEN}
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(token_data, f)
        cache_path = f.name

    try:
        sp_oauth = SpotifyOAuth(
            client_id=config.SPOTIFY_CLIENT_ID,
            client_secret=config.SPOTIFY_CLIENT_SECRET,
            redirect_uri="http://127.0.0.1:8888/callback",
            scope=" ".join(config.SCOPES),
            cache_path=cache_path,
        )
        token_info = sp_oauth.get_cached_token()
        if not token_info or not token_info.get("access_token"):
            token_info = sp_oauth.refresh_access_token(config.SPOTIFY_REFRESH_TOKEN)
        elif sp_oauth.is_token_expired(token_info):
            token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        return spotipy.Spotify(auth=token_info["access_token"])
    finally:
        try:
            os.unlink(cache_path)
        except OSError:
            pass


def get_initial_refresh_token() -> None:
    """
    Run this interactively (locally, not in CI) to get the initial refresh token.
    Opens browser for Spotify authorization.
    Prints the refresh token to console — user copies it to GitHub Secrets.

    Usage: python -c "from auth import get_initial_refresh_token; get_initial_refresh_token()"

    Requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in environment.
    Add http://127.0.0.1:8888/callback to your Spotify app's redirect URIs.
    """
    client_id = os.environ.get("SPOTIFY_CLIENT_ID") or input("SPOTIFY_CLIENT_ID: ").strip()
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET") or input("SPOTIFY_CLIENT_SECRET: ").strip()
    if not client_id or not client_secret:
        raise ValueError("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are required")
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://127.0.0.1:8888/callback",
        scope=" ".join(config.SCOPES),
        cache_path=".cache",
        show_dialog=True,
    )
    token_info = sp_oauth.get_access_token()
    if token_info and token_info.get("refresh_token"):
        print("=" * 60)
        print("SUCCESS! Your refresh token:")
        print("=" * 60)
        print(token_info["refresh_token"])
        print("=" * 60)
        print("\nAdd this as SPOTIFY_REFRESH_TOKEN in your GitHub Secrets.")
    else:
        print("Failed to obtain refresh token. Try again.")
