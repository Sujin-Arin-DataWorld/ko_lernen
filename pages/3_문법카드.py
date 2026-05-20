"""📝 문법카드 — Grammatikkarten (A1→B2)"""
import streamlit as st
import pandas as pd
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from lib.tts import VOICES, SPEED_PRESETS, get_cached_audio, audio_html
import streamlit.components.v1 as components

st.set_page_config(page_title="📝 문법 — Grammatik", page_icon="📝", layout="wide")

st.markdown("""
<style>
[data-testid="stVerticalBlock"]:has(.gfc-front),
[data-testid="stVerticalBlock"]:has(.gfc-back) {
    position: relative !important;
}
[data-testid="stVerticalBlock"]:has(.gfc-front) [data-testid="stForm"],
[data-testid="stVerticalBlock"]:has(.gfc-back)  [data-testid="stForm"] {
    position: absolute !important; top: 0 !important; left: 0 !important;
    right: 0 !important; height: 260px !important; border: none !important;
    padding: 0 !important; margin: 0 !important;
    background: transparent !important; z-index: 10 !important;
}
[data-testid="stVerticalBlock"]:has(.gfc-front) [data-testid="stForm"] *,
[data-testid="stVerticalBlock"]:has(.gfc-back)  [data-testid="stForm"] * {
    opacity: 0 !important; pointer-events: none !important;
}
[data-testid="stVerticalBlock"]:has(.gfc-front) [data-testid="stForm"] button,
[data-testid="stVerticalBlock"]:has(.gfc-back)  [data-testid="stForm"] button {
    pointer-events: auto !important; width: 100% !important;
    height: 260px !important; cursor: pointer !important;
    background: transparent !important;
}

[data-testid="stHorizontalBlock"]:has(.gfc-front) [data-testid="stColumn"]:first-child button,
[data-testid="stHorizontalBlock"]:has(.gfc-back)  [data-testid="stColumn"]:first-child button,
[data-testid="stHorizontalBlock"]:has(.gfc-front) [data-testid="stColumn"]:last-child button,
[data-testid="stHorizontalBlock"]:has(.gfc-back)  [data-testid="stColumn"]:last-child button {
    font-size: 1.8rem !important; height: 260px !important;
    background: transparent !important; border: none !important;
    color: #adb5bd !important;
}
[data-testid="stHorizontalBlock"]:has(.gfc-front) [data-testid="stColumn"]:first-child button:hover,
[data-testid="stHorizontalBlock"]:has(.gfc-back)  [data-testid="stColumn"]:first-child button:hover,
[data-testid="stHorizontalBlock"]:has(.gfc-front) [data-testid="stColumn"]:last-child button:hover,
[data-testid="stHorizontalBlock"]:has(.gfc-back)  [data-testid="stColumn"]:last-child button:hover {
    color: #f59f00 !important;
}

.gfc-front, .gfc-back {
    border-radius: 14px; padding: 2rem 1.5rem; min-height: 260px;
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; text-align: center; user-select: none;
    box-sizing: border-box;
}
.gfc-front {
    background: linear-gradient(135deg, #fff9db, #ffec99);
    border: 2px solid #f59f00;
}
.gfc-back {
    background: linear-gradient(135deg, #fff0f6, #fce4ec);
    border: 2px solid #e64980;
}
.gfc-pattern    { font-size: 2.2rem; font-weight: 700; color: #7d4a00; margin-bottom: .4rem; }
.gfc-type       { font-size: .9rem; color: #e67700; font-weight: 600; margin-bottom: .3rem; }
.gfc-level      { font-size: .75rem; font-weight: 700; color: #fff;
                  background: #f59f00; border-radius: 20px; padding: 2px 10px; margin-bottom: .6rem; }
.gfc-explanation{ font-size: 1.05rem; color: #495057; line-height: 1.6; margin-bottom: .6rem; }
.gfc-example    { font-size: 1rem; color: #880e4f; font-weight: 600; margin-bottom: .2rem; }
.gfc-german     { font-size: .95rem; color: #495057; font-style: italic; margin-bottom: .4rem; }
.gfc-note       { font-size: .82rem; color: #868e96; border-top: 1px solid #f8bbd0; padding-top: .4rem; margin-top: .2rem; }
.gfc-hint       { font-size: .9rem; color: #868e96; margin-top: .8rem; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in {"gram_idx": 0, "gram_flipped": False,
              "tts_voice_label": "Sun-Hi — Weiblich (Seoul)",
              "tts_speed_label": "📖 Lerntempo"}.items():
    st.session_state.setdefault(k, v)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Einstellungen")

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
    st.subheader("🔍 Filter")
    df_all = pd.read_csv(pathlib.Path(__file__).parent.parent / "data" / "grammar.csv")
    levels = ["Alle"] + sorted(df_all["level"].unique().tolist())
    sel_level = st.selectbox("Level", levels)
    types = ["Alle"] + sorted(df_all["type_de"].unique().tolist())
    sel_type = st.selectbox("Grammatiktyp", types)

    st.markdown("---")
    st.markdown("""
    **💡 Lerntipp:**
    1. Vorderseite = Grammatikmuster
    2. Rückseite = Erklärung + Beispiel
    3. Überlege erst selbst, dann umdrehen!
    """)

# ── Daten filtern ─────────────────────────────────────────────────────────────
df = df_all.copy()
if sel_level != "Alle":
    df = df[df["level"] == sel_level]
if sel_type != "Alle":
    df = df[df["type_de"] == sel_type]
df = df.reset_index(drop=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📝 문법카드 — Grammatik")
st.caption("Klicke auf die Karte, um Erklärung + Beispiel zu sehen")

if df.empty:
    st.warning("Keine Grammatik für diesen Filter.")
    st.stop()

idx = st.session_state.gram_idx % len(df)
st.session_state.gram_idx = idx
row = df.iloc[idx]

# Fortschritt
m1, m2 = st.columns(2)
m1.metric("Muster gesamt", len(df))
m2.metric("Aktuell", f"{idx+1} / {len(df)}")

# ── Level-Übersicht als Tabs ──────────────────────────────────────────────────
tab_all, tab_a1, tab_a2, tab_b1, tab_b2 = st.tabs(["🃏 Karten", "A1", "A2", "B1", "B2"])

with tab_all:
    flipped = st.session_state.gram_flipped

    if not flipped:
        card_html = f"""
        <div class="gfc-front">
            <div class="gfc-level">{row.level}</div>
            <div class="gfc-pattern">{row.pattern}</div>
            <div class="gfc-type">{row.type_de}</div>
            <div class="gfc-hint">👆 Tippen für Erklärung</div>
        </div>"""
    else:
        card_html = f"""
        <div class="gfc-back">
            <div class="gfc-level">{row.level}</div>
            <div class="gfc-pattern">{row.pattern}</div>
            <div class="gfc-type">{row.type_de}</div>
            <div class="gfc-explanation">{row.explanation_de}</div>
            <div class="gfc-example">{row.example_korean}</div>
            <div class="gfc-german">{row.example_german}</div>
            <div class="gfc-note">{row.note}</div>
        </div>"""

    _prev, _card, _next = st.columns([1, 8, 1])

    with _prev:
        if st.button("◀", key="gram_prev"):
            st.session_state.gram_idx = (idx - 1) % len(df)
            st.session_state.gram_flipped = False
            st.rerun()

    with _card:
        st.markdown(card_html, unsafe_allow_html=True)
        with st.form("gram_flip", clear_on_submit=False):
            if st.form_submit_button("flip", use_container_width=True):
                st.session_state.gram_flipped = not flipped
                st.rerun()

    with _next:
        if st.button("▶", key="gram_next"):
            st.session_state.gram_idx = (idx + 1) % len(df)
            st.session_state.gram_flipped = False
            st.rerun()

    # TTS für Beispielsatz
    if flipped:
        tts_c1, tts_c2, tts_c3 = st.columns([1, 2, 1])
        with tts_c2:
            if st.button("🔊 Beispiel hören", use_container_width=True):
                with st.spinner("Lade Audio…"):
                    audio = get_cached_audio(row.example_korean, voice, speed)
                    st.markdown(audio_html(audio), unsafe_allow_html=True)

    # Navigation
    st.markdown("---")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("⏮ Erste Karte", use_container_width=True, key="gram_first"):
            st.session_state.gram_idx = 0
            st.session_state.gram_flipped = False
            st.rerun()
    with b2:
        if st.button("🔀 Zufällig", use_container_width=True, key="gram_rand"):
            import random
            st.session_state.gram_idx = random.randint(0, len(df) - 1)
            st.session_state.gram_flipped = False
            st.rerun()
    with b3:
        if st.button("⏭ Letzte Karte", use_container_width=True, key="gram_last"):
            st.session_state.gram_idx = len(df) - 1
            st.session_state.gram_flipped = False
            st.rerun()

# ── Level-Tabs: Übersichtstabellen ───────────────────────────────────────────
for tab, lvl in zip([tab_a1, tab_a2, tab_b1, tab_b2], ["A1", "A2", "B1", "B2"]):
    with tab:
        subset = df_all[df_all["level"] == lvl][["pattern", "type_de", "explanation_de", "example_korean", "example_german"]]
        subset.columns = ["Muster", "Typ", "Erklärung", "Beispiel KO", "Beispiel DE"]
        st.dataframe(subset, use_container_width=True, hide_index=True)

# ── Swipe ─────────────────────────────────────────────────────────────────────
components.html("""
<script>
(function(){
    if (window.parent._gramSwipeReady) return;
    window.parent._gramSwipeReady = true;
    var sx = 0;
    var doc = window.parent.document;
    doc.addEventListener('touchstart', function(e){ sx = e.touches[0].clientX; }, {passive:true});
    doc.addEventListener('touchend', function(e){
        var dx = e.changedTouches[0].clientX - sx;
        if (Math.abs(dx) < 40) return;
        var label = dx < 0 ? '▶' : '◀';
        var btns = doc.querySelectorAll('button');
        for (var i = 0; i < btns.length; i++) {
            if (btns[i].textContent.trim() === label) { btns[i].click(); break; }
        }
    }, {passive:true});
})();
</script>
""", height=0)
