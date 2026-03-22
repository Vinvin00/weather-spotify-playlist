"""Blend mood with taste and fetch filtered recommendations."""

import random

import spotipy

import config


def blend_targets(mood: dict, taste: dict, ratio: float = 0.7) -> dict:
    """
    Blend weather mood targets with personal taste profile.

    For each audio feature:
        blended_target = (ratio * mood[feature]['target']) + ((1 - ratio) * taste['features'][feature])

    Keep min/max from mood (weather sets the boundaries, taste nudges the center).
    """
    blended = {}
    taste_feats = taste.get("features", {})

    for key, mood_val in mood.items():
        if isinstance(mood_val, dict) and "target" in mood_val:
            taste_val = taste_feats.get(key)
            if taste_val is not None:
                target = (ratio * mood_val["target"]) + ((1 - ratio) * taste_val)
            else:
                target = mood_val["target"]
            blended[key] = {
                "target": target,
                "min": mood_val["min"],
                "max": mood_val["max"],
            }
        else:
            blended[key] = mood_val

    return blended


def get_recommendations(
    sp: spotipy.Spotify,
    blended: dict,
    taste: dict,
    current_track_ids: set,
) -> list:
    """
    Fetch recommendations from Spotify and filter them.

    Returns list of track URIs (spotify:track:xxxx)
    """
    seed_artists = taste.get("seed_artists", [])[:2]
    seed_genres = taste.get("seed_genres", [])[:2]
    track_ids = list(taste.get("track_ids", set()))
    seed_track = random.choice(track_ids) if track_ids else None

    # Build recommendation params
    params = {
        "limit": config.CANDIDATE_POOL_SIZE,
    }
    if seed_artists:
        params["seed_artists"] = seed_artists
    if seed_genres:
        params["seed_genres"] = seed_genres
    if seed_track:
        params["seed_tracks"] = [seed_track]

    # Audio feature targets
    for key in ("energy", "valence", "danceability", "tempo", "acousticness", "instrumentalness"):
        if key in blended and isinstance(blended[key], dict):
            params[f"target_{key}"] = blended[key]["target"]
            params[f"min_{key}"] = blended[key]["min"]
            params[f"max_{key}"] = blended[key]["max"]

    result = sp.recommendations(**params)
    tracks = result.get("tracks", [])

    # Filter out: current playlist, user's top tracks, limit 2 per artist
    exclude_ids = current_track_ids | taste.get("track_ids", set())
    artist_counts = {}
    filtered = []

    for t in tracks:
        if not t or not t.get("uri"):
            continue
        tid = t.get("id")
        if tid and tid in exclude_ids:
            continue
        artist_id = t.get("artists", [{}])[0].get("id") if t.get("artists") else None
        if artist_id:
            count = artist_counts.get(artist_id, 0)
            if count >= 2:
                continue
            artist_counts[artist_id] = count + 1
        filtered.append(t)

    # Score by closeness to blended targets
    if len(filtered) <= config.PLAYLIST_SIZE:
        return [t["uri"] for t in filtered]

    feature_keys = ["energy", "valence", "danceability", "acousticness", "instrumentalness"]
    track_ids_to_score = [t["id"] for t in filtered]
    feats = sp.audio_features(track_ids_to_score)
    feat_map = {f["id"]: f for f in feats if f and f.get("id")}

    def score(track):
        tid = track.get("id")
        f = feat_map.get(tid) if tid else None
        if not f:
            return float("inf")
        s = 0
        for k in feature_keys:
            if k in blended and k in f and f[k] is not None:
                target = blended[k]["target"]
                s += (f[k] - target) ** 2
        if "tempo" in blended and f.get("tempo"):
            s += ((f["tempo"] - blended["tempo"]["target"]) / 100) ** 2
        return s

    filtered.sort(key=score)
    return [t["uri"] for t in filtered[: config.PLAYLIST_SIZE]]
