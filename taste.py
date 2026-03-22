"""Build user's taste profile from top tracks."""

from collections import Counter

import spotipy

import config


def build_taste_profile(sp: spotipy.Spotify) -> dict:
    """
    Analyze user's top tracks to extract average audio feature preferences.

    Returns dict:
        - features: dict of {feature_name: mean_value}
        - seed_artists: list of top 5 artist IDs
        - seed_genres: list of top 5 genres
        - track_ids: set of all top track IDs (for exclusion later)
    """
    result = sp.current_user_top_tracks(
        limit=config.TOP_TRACKS_LIMIT, time_range="medium_term"
    )
    items = result.get("items", [])
    if not items:
        return _empty_taste_profile()

    track_ids = []
    artist_ids = []
    all_genres = []

    for item in items:
        tid = item.get("id")
        if tid:
            track_ids.append(tid)
        for artist in item.get("artists", []):
            aid = artist.get("id")
            if aid:
                artist_ids.append(aid)
                # Get artist details for genres
                try:
                    art = sp.artist(aid)
                    for g in art.get("genres", []):
                        all_genres.append(g)
                except Exception:
                    pass

    # Audio features (batch of 100 max)
    features_list = []
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i : i + 100]
        feats = sp.audio_features(batch)
        for f in feats:
            if f and f.get("id"):
                features_list.append(f)

    # Mean for each feature
    feature_keys = ["energy", "valence", "danceability", "tempo", "acousticness", "instrumentalness"]
    features = {}
    for key in feature_keys:
        vals = [f[key] for f in features_list if f.get(key) is not None]
        if key == "tempo":
            features[key] = sum(vals) / len(vals) if vals else 100
        else:
            features[key] = sum(vals) / len(vals) if vals else 0.5

    # Top 5 artists by frequency
    artist_counts = Counter(artist_ids)
    seed_artists = [a for a, _ in artist_counts.most_common(5)]

    # Top 5 genres by frequency (filter empty/invalid)
    genre_counts = Counter(g for g in all_genres if g and isinstance(g, str))
    seed_genres = [g for g, _ in genre_counts.most_common(5)]

    # Spotify recommendations needs valid seed genres from their list
    # Filter to known genres if needed
    valid_genres = {
        "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime",
        "black-metal", "bluegrass", "blues", "bossanova", "brazil", "breakbeat",
        "british", "cantopop", "chicago-house", "children", "chill", "classical",
        "club", "comedy", "country", "dance", "dancehall", "death-metal",
        "deep-house", "detroit-techno", "disco", "disney", "drum-and-bass",
        "dub", "dubstep", "edm", "electro", "electronic", "emo", "folk",
        "forro", "french", "funk", "garage", "german", "gospel", "goth",
        "grindcore", "groove", "grunge", "guitar", "happy", "hard-rock",
        "hardcore", "hardstyle", "heavy-metal", "hip-hop", "holidays",
        "honky-tonk", "house", "idm", "indian", "indie", "indie-pop",
        "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock",
        "jazz", "k-pop", "kids", "latin", "latino", "malay", "mandopop",
        "metal", "metal-misc", "metalcore", "minimal-techno", "movies",
        "mpb", "new-age", "new-release", "opera", "pagode", "party",
        "philippines-opm", "piano", "pop", "pop-film", "post-dubstep",
        "power-pop", "progressive-house", "psych-rock", "punk", "punk-rock",
        "r-n-b", "rainy-day", "reggae", "reggaeton", "road-trip", "rock",
        "romance", "sad", "salsa", "samba", "sertanejo", "show-tunes",
        "singer-songwriter", "ska", "sleep", "songwriter", "soul",
        "soundtracks", "spanish", "study", "summer", "swedish", "synth-pop",
        "tango", "techno", "trance", "trip-hop", "turkish", "work-out",
        "world-music",
    }
    seed_genres = [g for g in seed_genres if g.lower() in valid_genres][:5]
    if not seed_genres:
        seed_genres = ["pop", "indie"]  # fallback

    return {
        "features": features,
        "seed_artists": seed_artists[:5],
        "seed_genres": seed_genres[:5],
        "track_ids": set(track_ids),
    }


def _empty_taste_profile() -> dict:
    """Return fallback profile when user has no top tracks."""
    return {
        "features": {
            "energy": 0.5,
            "valence": 0.5,
            "danceability": 0.5,
            "tempo": 100,
            "acousticness": 0.5,
            "instrumentalness": 0.1,
        },
        "seed_artists": [],
        "seed_genres": ["pop", "indie"],
        "track_ids": set(),
    }
