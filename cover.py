"""Generate and upload dynamic playlist cover image based on weather."""

import base64
import io
import math
import random

import spotipy
from PIL import Image, ImageDraw, ImageFont

import config


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load font with fallback for GitHub Actions (Ubuntu)."""
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size)
        except OSError:
            return ImageFont.load_default()


def _draw_sun(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int) -> None:
    """Draw sun: yellow circle with radiating lines."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#FFD700", outline="#FFA500")
    for i in range(12):
        angle = i * 30
        rad = math.radians(angle)
        x1 = cx + (r + 5) * math.cos(rad)
        y1 = cy + (r + 5) * math.sin(rad)
        x2 = cx + (r + 25) * math.cos(rad)
        y2 = cy + (r + 25) * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill="#FFA500", width=3)


def _draw_cloud(draw: ImageDraw.ImageDraw, cx: int, cy: int, color: str = "#95a5a6") -> None:
    """Draw cloud: overlapping ellipses."""
    for dx, dy, w, h in [(0, 0, 80, 50), (-40, -20, 60, 45), (35, -25, 55, 40), (-15, 10, 70, 45)]:
        draw.ellipse([cx + dx - w // 2, cy + dy - h // 2, cx + dx + w // 2, cy + dy + h // 2], fill=color)


def _draw_rain(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """Draw rain: cloud + diagonal lines."""
    _draw_cloud(draw, cx, cy - 30, "#7f8c8d")
    for i in range(-3, 4):
        for j in range(3):
            x1 = cx + i * 25
            y1 = cy + j * 30
            draw.line([(x1, y1), (x1 + 15, y1 + 25)], fill="#3498db", width=3)


def _draw_snow(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """Draw snow: cloud + white dots."""
    _draw_cloud(draw, cx, cy - 30, "#bdc3c7")
    rng = random.Random(42)
    for _ in range(25):
        x = cx + rng.randint(-100, 100)
        y = cy + rng.randint(-50, 100)
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill="#ecf0f1")


def _draw_thunder(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """Draw thunder: cloud + yellow zigzag."""
    _draw_cloud(draw, cx, cy - 30, "#4a4a6a")
    points = [(cx - 20, cy - 10), (cx, cy + 40), (cx + 10, cy + 20), (cx + 30, cy + 60), (cx + 5, cy + 50)]
    draw.line(points, fill="#FFD700", width=5, joint="curve")


def generate_cover(weather: dict) -> str:
    """
    Generate a 640x640 JPEG cover image reflecting the weather.

    Returns base64-encoded JPEG string for Spotify API.
    """
    w, h = 640, 640
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    code = weather.get("weather_code", 0)
    temp = weather.get("temperature", 0)
    is_day = weather.get("is_day", True)

    # Background gradient (simplified: two rectangles)
    if 95 <= code <= 99:
        c1, c2 = "#2d1b69", "#11001c"
    elif code in (45, 48):
        c1, c2 = "#d5d5d5", "#f0f0f0"
    elif 71 <= code <= 75:
        c1, c2 = "#ecf0f1", "#bdc3c7"
    elif 61 <= code <= 65 or 80 <= code <= 82 or 51 <= code <= 55:
        c1, c2 = "#2c3e50", "#3498db"
    elif code in (1, 2, 3):
        c1, c2 = "#95a5a6", "#7f8c8d"
    elif code == 0 and is_day:
        c1, c2 = "#FFB347", "#FF6B6B"
    elif code == 0 and not is_day:
        c1, c2 = "#1a1a2e", "#16213e"
    else:
        c1, c2 = "#95a5a6", "#7f8c8d"

    for y in range(h):
        t = y / h
        r = int(int(c1[1:3], 16) * (1 - t) + int(c2[1:3], 16) * t)
        g = int(int(c1[3:5], 16) * (1 - t) + int(c2[3:5], 16) * t)
        b = int(int(c1[5:7], 16) * (1 - t) + int(c2[5:7], 16) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Weather icon
    cx, cy = w // 2, h // 2 - 40
    if 95 <= code <= 99:
        _draw_thunder(draw, cx, cy)
    elif 71 <= code <= 75:
        _draw_snow(draw, cx, cy)
    elif 61 <= code <= 65 or 80 <= code <= 82 or 51 <= code <= 55:
        _draw_rain(draw, cx, cy)
    elif code in (45, 48):
        _draw_cloud(draw, cx, cy, "#9e9e9e")
    elif code in (1, 2, 3):
        _draw_cloud(draw, cx, cy)
        if is_day:
            _draw_sun(draw, cx - 80, cy - 60, 25)
    else:
        if is_day:
            _draw_sun(draw, cx, cy - 20, 50)
        else:
            draw.ellipse([cx - 40, cy - 60, cx + 40, cy + 20], fill="#e8e8e8", outline="#c0c0c0")

    # Text
    font_large = _get_font(72)
    font_small = _get_font(32)
    temp_str = f"{int(round(temp))}°C"
    draw.text((w // 2 - 60, h - 180), temp_str, fill="#ffffff", font=font_large)
    draw.text((w // 2 - 50, h - 100), "Segovia", fill="#ffffff", font=font_small)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def upload_cover(sp: spotipy.Spotify, image_b64: str) -> None:
    """
    Upload cover image to the playlist.

    image_b64: base64-encoded JPEG string (no data:image prefix)
    """
    sp.playlist_upload_cover_image(config.PLAYLIST_ID, image_b64)
