#!/usr/bin/env python3
"""
Interactive setup script for Weather Playlist.
Run this once to get your Spotify refresh token and see what GitHub Secrets to add.

Usage: python3 setup.py
"""

import subprocess
import sys

# Ensure spotipy is installed
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    print("Installing spotipy...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "spotipy", "--quiet"])
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth


def main():
    print()
    print("=" * 55)
    print("  🌤️  Weather Playlist — Setup")
    print("=" * 55)
    print()
    print("This script will help you get everything configured.")
    print("You'll need your Spotify app credentials ready.")
    print("(Create an app at https://developer.spotify.com/dashboard)")
    print()
    print("IMPORTANT: Make sure you've added this Redirect URI")
    print("in your Spotify app settings:")
    print()
    print("  http://127.0.0.1:8888/callback")
    print()

    # Get credentials
    client_id = input("Enter your Spotify Client ID: ").strip()
    if not client_id:
        print("❌ Client ID cannot be empty.")
        return

    client_secret = input("Enter your Spotify Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret cannot be empty.")
        return

    # Get playlist ID
    print()
    print("Now enter your Spotify playlist ID.")
    print("You can find it by right-clicking a playlist in Spotify →")
    print("Share → Copy link. The ID is the part after 'playlist/'.")
    print("Example: https://open.spotify.com/playlist/ABC123... → ABC123...")
    print()
    playlist_id = input("Enter your Playlist ID (or press Enter to create one later): ").strip()

    # Authenticate
    print()
    print("Opening your browser for Spotify authorization...")
    print("(If it doesn't open, check your terminal for a URL to paste)")
    print()

    scopes = "user-top-read playlist-modify-public playlist-modify-private ugc-image-upload"

    try:
        sp_oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://127.0.0.1:8888/callback",
            scope=scopes,
            open_browser=True
        )

        # This triggers the browser flow
        token_info = sp_oauth.get_access_token(as_dict=True)

        if not token_info or "refresh_token" not in token_info:
            print("❌ Failed to get refresh token. Please try again.")
            return

        refresh_token = token_info["refresh_token"]

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print()
        print("Common fixes:")
        print("  - Make sure http://127.0.0.1:8888/callback is in your Spotify app's Redirect URIs")
        print("  - Make sure your Client ID and Secret are correct")
        print("  - Try running this script again")
        return

    # Verify it works
    print()
    print("✅ Authentication successful!")

    try:
        sp = spotipy.Spotify(auth=token_info["access_token"])
        user = sp.current_user()
        print(f"   Logged in as: {user['display_name']} ({user['id']})")
    except Exception:
        print("   (Couldn't verify user, but token was obtained)")

    # Show results
    print()
    print("=" * 55)
    print("  📋  Add these as GitHub Secrets")
    print("=" * 55)
    print()
    print("Go to your GitHub repo → Settings → Secrets and variables → Actions")
    print("Click 'New repository secret' for each one:")
    print()
    print(f"  Name:  SPOTIFY_CLIENT_ID")
    print(f"  Value: {client_id}")
    print()
    print(f"  Name:  SPOTIFY_CLIENT_SECRET")
    print(f"  Value: {client_secret}")
    print()
    print(f"  Name:  SPOTIFY_REFRESH_TOKEN")
    print(f"  Value: {refresh_token}")
    print()
    if playlist_id:
        print(f"  Name:  PLAYLIST_ID")
        print(f"  Value: {playlist_id}")
    else:
        print("  Name:  PLAYLIST_ID")
        print("  Value: (create a playlist in Spotify, then get its ID)")
    print()
    print("=" * 55)
    print("  🎉  Setup complete!")
    print("=" * 55)
    print()
    print("Next steps:")
    print("  1. Add the 4 secrets above to GitHub")
    print("  2. Push your code:  git add . && git commit -m 'Setup' && git push")
    print("  3. Go to Actions tab → Run workflow")
    print("  4. Check your Spotify playlist!")
    print()


if __name__ == "__main__":
    main()