"""Build user's taste profile from top tracks and artists. NO audio features."""

from collections import Counter

import spotipy

import config


def build_taste_profile(sp: spotipy.Spotify) -> dict:
    """
    Get user's top artists and tracks. NO audio features.

    Steps:
    1. Fetch top 50 tracks: sp.current_user_top_tracks(limit=50, time_range='medium_term')
    2. Fetch top 20 artists: sp.current_user_top_artists(limit=20, time_range='medium_term')
    3. Extract genres from top artists (flatten all genres into a list, count occurrences)
    4. Get top 5 most common genres

    Returns dict:
        - top_track_ids: set of track IDs (for exclusion — don't recommend songs user already knows)
        - top_artist_ids: list of artist IDs
        - top_genres: list of top 5 genres (most listened to)
        - top_artist_names: list of artist names (for search queries)
    """
    track_ids = []
    top_artist_ids = []
    top_artist_names = []
    all_genres = []

    # 1. Top tracks
    try:
        tracks_result = sp.current_user_top_tracks(
            limit=config.TOP_TRACKS_LIMIT, time_range="medium_term"
        )
        for item in tracks_result.get("items", []):
            if item.get("id"):
                track_ids.append(item["id"])
    except Exception:
        pass

    # 2. Top artists
    try:
        artists_result = sp.current_user_top_artists(
            limit=20, time_range="medium_term"
        )
        for artist in artists_result.get("items", []):
            if artist.get("id"):
                top_artist_ids.append(artist["id"])
            if artist.get("name"):
                top_artist_names.append(artist["name"])
            for g in artist.get("genres", []):
                if g and isinstance(g, str):
                    all_genres.append(g)
    except Exception:
        pass

    # 3 & 4. Top 5 genres by occurrence
    genre_counts = Counter(all_genres)
    top_genres = [g for g, _ in genre_counts.most_common(5)]

    if not top_genres:
        top_genres = ["pop", "indie"]

    return {
        "top_track_ids": set(track_ids),
        "top_artist_ids": top_artist_ids[:10],
        "top_genres": top_genres[:5],
        "top_artist_names": top_artist_names[:10],
    }
