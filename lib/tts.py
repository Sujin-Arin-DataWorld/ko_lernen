"""Koreanische TTS — edge-tts (Microsoft Neural, kostenlos)"""
import asyncio, base64, os, tempfile
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
DEFAULT_VOICE  = "ko-KR-SunHiNeural"
DEFAULT_RATE   = "-15%"
SAMPLE_TEXT    = "안녕하세요! 저는 한국어를 공부해요."

async def _synth(text, voice, rate):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp.close()
    try:
        await edge_tts.Communicate(text, voice, rate=rate).save(tmp.name)
        return open(tmp.name, "rb").read()
    finally:
        try: os.unlink(tmp.name)
        except OSError: pass

def synthesize(text, voice=DEFAULT_VOICE, rate=DEFAULT_RATE):
    return asyncio.run(_synth(text, voice, rate))

def audio_html(audio_bytes, compact=False):
    b64 = base64.b64encode(audio_bytes).decode()
    uid = abs(hash(audio_bytes[:32])) % 1_000_000
    h   = "36px" if compact else "54px"
    return (
        f'<audio id="aud_{uid}" controls autoplay '
        f'style="width:100%;height:{h};margin:.25rem 0">'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    )

def get_cached_audio(text, voice, rate):
    import streamlit as st
    st.session_state.setdefault("tts_cache", {})
    key = (text[:80], voice, rate)
    if key not in st.session_state.tts_cache:
        st.session_state.tts_cache[key] = synthesize(text, voice, rate)
    return st.session_state.tts_cache[key]
