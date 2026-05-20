"""📚 단어장 — Koreanische Vokabelkarten (A1→B2)"""
import streamlit as st
import pandas as pd
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from lib.tts import VOICES, SPEED_PRESETS, get_cached_audio, audio_html
import streamlit.components.v1 as components

st.set_page_config(page_title="📚 단어장 — Vokabeln", page_icon="📚", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Kartencontainer ── */
[data-testid="stVerticalBlock"]:has(.fc-front),
[data-testid="stVerticalBlock"]:has(.fc-back) {
    position: relative !important;
}
[data-testid="stVerticalBlock"]:has(.fc-front) [data-testid="stForm"],
[data-testid="stVerticalBlock"]:has(.fc-back)  [data-testid="stForm"] {
    position: absolute !important; top: 0 !important; left: 0 !important;
    right: 0 !important; height: 220px !important; border: none !important;
    padding: 0 !important; margin: 0 !important;
    background: transparent !important; z-index: 10 !important;
}
[data-testid="stVerticalBlock"]:has(.fc-front) [data-testid="stForm"] *,
[data-testid="stVerticalBlock"]:has(.fc-back)  [data-testid="stForm"] * {
    opacity: 0 !important; pointer-events: none !important;
}
[data-testid="stVerticalBlock"]:has(.fc-front) [data-testid="stForm"] button,
[data-testid="stVerticalBlock"]:has(.fc-back)  [data-testid="stForm"] button {
    pointer-events: auto !important; width: 100% !important;
    height: 220px !important; cursor: pointer !important;
    background: transparent !important;
}

/* ── Vokabelkarte ── */
.fc-front, .fc-back {
    border-radius: 14px; padding: 2rem 1.5rem; min-height: 220px;
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; text-align: center; user-select: none;
    box-sizing: border-box;
}
.fc-front {
    background: linear-gradient(135deg, #e7f5ff, #d0ebff);
    border: 2px solid #339af0;
}
.fc-back {
    background: linear-gradient(135deg, #ebfbee, #d3f9d8);
    border: 2px solid #51cf66;
}
.fc-korean   { font-size: 2.8rem; font-weight: 700; color: #1864ab; margin-bottom: .3rem; }
.fc-roman    { font-size: 1.1rem; color: #4c9fd6; margin-bottom: .5rem; font-style: italic; }
.fc-german   { font-size: 1.8rem; font-weight: 700; color: #2b8a3e; margin-bottom: .3rem; }
.fc-pos      { font-size: .85rem; color: #868e96; margin-bottom: .2rem; }
.fc-example  { font-size: .95rem; color: #495057; margin-top: .6rem; line-height: 1.5; }
.fc-level    { font-size: .75rem; font-weight: 700; color: #fff;
               background: #339af0; border-radius: 20px; padding: 2px 10px; margin-bottom: .5rem; }
.fc-hint     { font-size: .9rem; color: #868e96; margin-top: .5rem; }

/* ── Seitennavigation (◀ ▶) ── */
[data-testid="stHorizontalBlock"]:has(.fc-front) [data-testid="stColumn"]:first-child button,
[data-testid="stHorizontalBlock"]:has(.fc-back)  [data-testid="stColumn"]:first-child button,
[data-testid="stHorizontalBlock"]:has(.fc-front) [data-testid="stColumn"]:last-child button,
[data-testid="stHorizontalBlock"]:has(.fc-back)  [data-testid="stColumn"]:last-child button {
    font-size: 1.8rem !important; height: 220px !important;
    background: transparent !important; border: none !important;
    color: #adb5bd !important; transition: color .15s;
}
[data-testid="stHorizontalBlock"]:has(.fc-front) [data-testid="stColumn"]:first-child button:hover,
[data-testid="stHorizontalBlock"]:has(.fc-back)  [data-testid="stColumn"]:first-child button:hover,
[data-testid="stHorizontalBlock"]:has(.fc-front) [data-testid="stColumn"]:last-child button:hover,
[data-testid="stHorizontalBlock"]:has(.fc-back)  [data-testid="stColumn"]:last-child button:hover {
    color: #339af0 !important;
}

/* ── Fortschrittsbalken ── */
.prog-bar { height: 6px; border-radius: 3px; background: #dee2e6; margin: .5rem 0 1rem; }
.prog-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #339af0, #51cf66); transition: width .3s; }

/* ── Statistik-Chips ── */
.stat-chip { display: inline-block; border-radius: 20px; padding: 3px 12px;
             font-size: .82rem; font-weight: 600; margin: 2px; }
.chip-seen    { background: #e7f5ff; color: #1864ab; }
.chip-correct { background: #ebfbee; color: #2b8a3e; }
.chip-skip    { background: #fff9db; color: #7d4a00; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
_DEF = {
    "vok_idx":      0,
    "vok_flipped":  False,
    "vok_correct":  0,
    "vok_skipped":  0,
    "vok_seen_ids": [],
    "tts_voice_label": "Sun-Hi — Weiblich (Seoul)",
    "tts_speed_label": "📖 Lerntempo",
}
for k, v in _DEF.items():
    st.session_state.setdefault(k, v)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Einstellungen")

    # TTS
    st.subheader("🔊 Aussprache")
    voice_label = st.selectbox("Stimme", list(VOICES.keys()),
                                index=list(VOICES.keys()).index(st.session_state.tts_voice_label))
    speed_label = st.selectbox("Geschwindigkeit", list(SPEED_PRESETS.keys()),
                                index=list(SPEED_PRESETS.keys()).index(st.session_state.tts_speed_label))
    st.session_state.tts_voice_label = voice_label
    st.session_state.tts_speed_label = speed_label
    voice = VOICES[voice_label]
    speed = f"{SPEED_PRESETS[speed_label]:+d}%"

    st.markdown("---")

    # Filter
    st.subheader("🔍 Filter")
    df_all = pd.read_csv(pathlib.Path(__file__).parent.parent / "data" / "korean_vocab.csv")

    levels = ["Alle"] + sorted(df_all["level"].unique().tolist())
    sel_level = st.selectbox("Level", levels)

    topics_raw = sorted(df_all["topic"].unique().tolist())
    sel_topic = st.selectbox("Thema", ["Alle"] + topics_raw)

    pos_raw = sorted(df_all["pos_de"].unique().tolist())
    sel_pos = st.selectbox("Wortart", ["Alle"] + pos_raw)

    st.markdown("---")

    # Kartenrichtung
    st.subheader("🔄 Kartenrichtung")
    direction = st.radio("Vorderseite zeigt", ["🇰🇷 Koreanisch → 🇩🇪 Deutsch", "🇩🇪 Deutsch → 🇰🇷 Koreanisch"])

    st.markdown("---")

    if st.button("🔄 Statistik zurücksetzen"):
        st.session_state.vok_correct = 0
        st.session_state.vok_skipped = 0
        st.session_state.vok_seen_ids = []
        st.rerun()

# ── Daten filtern ─────────────────────────────────────────────────────────────
df = df_all.copy()
if sel_level != "Alle":
    df = df[df["level"] == sel_level]
if sel_topic != "Alle":
    df = df[df["topic"] == sel_topic]
if sel_pos != "Alle":
    df = df[df["pos_de"] == sel_pos]
df = df.reset_index(drop=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📚 단어장 — Vokabeln")
st.caption("Klicke auf die Karte zum Umdrehen · Wische links/rechts auf dem Handy")

if df.empty:
    st.warning("Keine Vokabeln für diesen Filter. Bitte Einstellungen anpassen.")
    st.stop()

# Index prüfen
idx = st.session_state.vok_idx % len(df)
st.session_state.vok_idx = idx
row = df.iloc[idx]

# Fortschritt
seen = len(set(st.session_state.vok_seen_ids))
pct = seen / len(df_all) * 100
st.markdown(
    f'<div class="prog-bar"><div class="prog-fill" style="width:{pct:.0f}%"></div></div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Karten gesamt", len(df))
c2.metric("Karte", f"{idx+1} / {len(df)}")
c3.metric("✅ Richtig", st.session_state.vok_correct)
c4.metric("⏭ Übersprungen", st.session_state.vok_skipped)

# ── Karte ─────────────────────────────────────────────────────────────────────
flipped = st.session_state.vok_flipped
ko_first = "Koreanisch" in direction

if ko_first:
    front_html = f"""
    <div class="fc-front">
        <div class="fc-level">{row.level}</div>
        <div class="fc-korean">{row.korean}</div>
        <div class="fc-roman">[{row.romanization}]</div>
        <div class="fc-pos">{row.pos_de}</div>
        <div class="fc-hint">👆 Tippen zum Umdrehen</div>
    </div>"""
    back_html = f"""
    <div class="fc-back">
        <div class="fc-level">{row.level}</div>
        <div class="fc-german">{row.german}</div>
        <div class="fc-pos">{row.pos_de} · {row.topic}</div>
        <div class="fc-example">
            <em>{row.example_korean}</em><br>
            {row.example_german}
        </div>
    </div>"""
else:
    front_html = f"""
    <div class="fc-front">
        <div class="fc-level">{row.level}</div>
        <div class="fc-german">{row.german}</div>
        <div class="fc-pos">{row.pos_de}</div>
        <div class="fc-hint">👆 Tippen zum Umdrehen</div>
    </div>"""
    back_html = f"""
    <div class="fc-back">
        <div class="fc-level">{row.level}</div>
        <div class="fc-korean">{row.korean}</div>
        <div class="fc-roman">[{row.romanization}]</div>
        <div class="fc-pos">{row.pos_de} · {row.topic}</div>
        <div class="fc-example">
            <em>{row.example_korean}</em><br>
            {row.example_german}
        </div>
    </div>"""

card_html = back_html if flipped else front_html

# 3-Spalten-Layout: ◀ Karte ▶
_prev_col, _card_col, _next_col = st.columns([1, 8, 1])

with _prev_col:
    if st.button("◀", key="nav_prev"):
        st.session_state.vok_idx = (idx - 1) % len(df)
        st.session_state.vok_flipped = False
        st.rerun()

with _card_col:
    st.markdown(card_html, unsafe_allow_html=True)
    with st.form("flip_form", clear_on_submit=False):
        if st.form_submit_button("flip", use_container_width=True):
            st.session_state.vok_flipped = not flipped
            if not flipped:
                seen_ids = st.session_state.vok_seen_ids
                if row.korean not in seen_ids:
                    seen_ids.append(row.korean)
                    st.session_state.total_cards_seen = st.session_state.get("total_cards_seen", 0) + 1
                    st.session_state.cards_flipped = st.session_state.get("cards_flipped", 0) + 1
            st.rerun()

with _next_col:
    if st.button("▶", key="nav_next"):
        st.session_state.vok_idx = (idx + 1) % len(df)
        st.session_state.vok_flipped = False
        st.rerun()

# ── TTS ───────────────────────────────────────────────────────────────────────
tts_col1, tts_col2, tts_col3 = st.columns([1, 2, 1])
with tts_col2:
    if st.button("🔊 Aussprache hören", use_container_width=True, key="tts_btn"):
        with st.spinner("Lade Audio…"):
            audio = get_cached_audio(row.korean, voice, speed)
            st.markdown(audio_html(audio), unsafe_allow_html=True)

    if flipped:
        example_col1, example_col2 = st.columns(2)
        with example_col1:
            if st.button("✅ Gewusst!", use_container_width=True, key="correct_btn"):
                st.session_state.vok_correct += 1
                st.session_state.correct_answers = st.session_state.get("correct_answers", 0) + 1
                st.session_state.vok_idx = (idx + 1) % len(df)
                st.session_state.vok_flipped = False
                st.rerun()
        with example_col2:
            if st.button("⏭ Überspringen", use_container_width=True, key="skip_btn"):
                st.session_state.vok_skipped += 1
                st.session_state.vok_idx = (idx + 1) % len(df)
                st.session_state.vok_flipped = False
                st.rerun()

# ── Bottom-Navigation ─────────────────────────────────────────────────────────
st.markdown("---")
b1, b2, b3 = st.columns(3)
with b1:
    if st.button("⏮ Erste Karte", use_container_width=True):
        st.session_state.vok_idx = 0
        st.session_state.vok_flipped = False
        st.rerun()
with b2:
    if st.button("🔀 Zufällig", use_container_width=True):
        import random
        st.session_state.vok_idx = random.randint(0, len(df) - 1)
        st.session_state.vok_flipped = False
        st.rerun()
with b3:
    if st.button("⏭ Letzte Karte", use_container_width=True):
        st.session_state.vok_idx = len(df) - 1
        st.session_state.vok_flipped = False
        st.rerun()

# ── Swipe-Gesten (Mobile) ────────────────────────────────────────────────────
components.html("""
<script>
(function(){
    if (window.parent._vokSwipeReady) return;
    window.parent._vokSwipeReady = true;
    var sx = 0, sy = 0;
    var doc = window.parent.document;
    doc.addEventListener('touchstart', function(e){
        sx = e.touches[0].clientX; sy = e.touches[0].clientY;
    }, {passive:true});
    doc.addEventListener('touchend', function(e){
        var dx = e.changedTouches[0].clientX - sx;
        var dy = e.changedTouches[0].clientY - sy;
        if (Math.abs(dx) < 40 || Math.abs(dy) > Math.abs(dx)) return;
        var label = dx < 0 ? '▶' : '◀';
        var btns = doc.querySelectorAll('button');
        for (var i = 0; i < btns.length; i++) {
            if (btns[i].textContent.trim() === label) {
                btns[i].click(); break;
            }
        }
    }, {passive:true});
})();
</script>
""", height=0)

# ── Vokabelliste ──────────────────────────────────────────────────────────────
with st.expander("📋 Alle Vokabeln dieser Auswahl anzeigen"):
    show_df = df[["korean", "romanization", "german", "level", "pos_de", "topic"]].copy()
    show_df.columns = ["Koreanisch", "Romanisierung", "Deutsch", "Level", "Wortart", "Thema"]
    st.dataframe(show_df, use_container_width=True, hide_index=True)
