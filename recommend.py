"""Build playlist using Spotify search — no deprecated recommendations/audio-features endpoints."""

import random

import spotipy

import config


def get_recommendations(
    sp: spotipy.Spotify,
    mood: dict,
    taste: dict,
    current_track_ids: set,
) -> list:
    """
    Build a playlist using Spotify search, blending weather mood with personal taste.

    Strategy: Run multiple search queries combining mood keywords with user's
    favorite genres/artists.
    """
    keywords = mood.get("keywords", [])
    genres = mood.get("genres", [])
    vibe = mood.get("vibe", "mellow")
    top_genres = taste.get("top_genres", [])
    top_artist_names = taste.get("top_artist_names", [])
    exclude_ids = current_track_ids | taste.get("top_track_ids", set())

    if not keywords:
        keywords = ["mellow", "indie"]

    # Build 6-8 search queries
    queries = []

    # Type A: Mood + user's genre (3 queries)
    for genre in (top_genres or ["pop", "indie"])[:3]:
        kw = random.choice(keywords)
        queries.append(f"genre:{genre} {kw}")

    # Type B: Artist name + mood vibe (2 queries)
    for name in (top_artist_names or [])[:2]:
        queries.append(f"{name} {vibe}")

    # Type C: Mood genre not in user's top + mood keyword (2 queries)
    mood_only_genres = [g for g in genres if g not in (top_genres or [])]
    for genre in (mood_only_genres or genres)[:2]:
        kw = random.choice(keywords)
        queries.append(f"genre:{genre} {kw}")

    # Execute searches and collect tracks
    all_tracks = []
    seen_ids = set()
    artist_counts = {}

    for query in queries:
        try:
            results = sp.search(q=query, type="track", limit=10)
            items = results.get("tracks", {}).get("items", [])
            for track in items:
                if not track or not track.get("uri"):
                    continue
                tid = track.get("id")
                if not tid or tid in exclude_ids or tid in seen_ids:
                    continue
                artist_id = (
                    track.get("artists", [{}])[0].get("id")
                    if track.get("artists")
                    else None
                )
                if artist_id:
                    count = artist_counts.get(artist_id, 0)
                    if count >= 2:
                        continue
                    artist_counts[artist_id] = count + 1
                seen_ids.add(tid)
                all_tracks.append(track)
        except Exception:
            continue

    random.shuffle(all_tracks)
    return [t["uri"] for t in all_tracks[: config.PLAYLIST_SIZE]]
