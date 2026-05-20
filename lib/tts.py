"""Koreanische TTS — edge-tts (Microsoft Neural, kostenlos).

Zwei-Stufen-Cache:
  1. Memory (Streamlit session_state) — sofortiger Treffer in derselben Session
  2. Disk (~/.cache/ko_lernen_tts) — überlebt App-Restart
"""
import asyncio, base64, hashlib, os
from collections import OrderedDict
from pathlib import Path
import edge_tts

VOICES = {
    "Sun-Hi — Weiblich (Seoul)": "ko-KR-SunHiNeural",
    "In-Joon — Männlich (Seoul)": "ko-KR-InJoonNeural",
}
SPEED_PRESETS = {
    "🐌 Sehr langsam": -30,
    "📖 Lerntempo":    -15,
    "▶ Normal":          0,
    "⚡ Schnell":      +15,
}
DEFAULT_VOICE = "ko-KR-SunHiNeural"
DEFAULT_RATE  = "-15%"
SAMPLE_TEXT   = "안녕하세요! 저는 한국어를 공부해요."

_MEM_CACHE_MAX = 200
CACHE_DIR = Path.home() / ".cache" / "ko_lernen_tts"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(text: str, voice: str, rate: str) -> Path:
    key = hashlib.md5(f"{text}|{voice}|{rate}".encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{key}.mp3"


async def _synth_to_disk(text: str, voice: str, rate: str, path: Path) -> bytes:
    await edge_tts.Communicate(text, voice, rate=rate).save(str(path))
    return path.read_bytes()


def synthesize(text: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE) -> bytes:
    path = _cache_path(text, voice, rate)
    if path.exists():
        try:
            return path.read_bytes()
        except OSError:
            pass
    return asyncio.run(_synth_to_disk(text, voice, rate, path))


def audio_html(audio_bytes: bytes, compact: bool = False) -> str:
    b64 = base64.b64encode(audio_bytes).decode()
    uid = abs(hash(audio_bytes[:32])) % 1_000_000
    h   = "36px" if compact else "54px"
    return (
        f'<audio id="aud_{uid}" controls autoplay '
        f'style="width:100%;height:{h};margin:.25rem 0">'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    )


def get_cached_audio(text: str, voice: str, rate: str) -> bytes:
    """Memory-Cache (session_state) vor Disk-Cache vor Synthese."""
    import streamlit as st
    cache: "OrderedDict[tuple, bytes]" = st.session_state.setdefault("tts_cache", OrderedDict())
    key = (text[:120], voice, rate)
    hit = cache.get(key)
    if hit is not None:
        cache.move_to_end(key)
        return hit
    audio = synthesize(text, voice, rate)
    cache[key] = audio
    cache.move_to_end(key)
    while len(cache) > _MEM_CACHE_MAX:
        cache.popitem(last=False)
    return audio
