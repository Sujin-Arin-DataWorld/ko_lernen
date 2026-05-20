"""📝 문법카드 — Grammatikkarten (A1→B2)"""
import random
import sys, pathlib
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from lib.tts import VOICES, SPEED_PRESETS, get_cached_audio, audio_html
from lib.data import load_grammar
from lib.user import require_user

st.set_page_config(
    page_title="📝 문법",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in {
    "gram_idx":         0,
    "gram_flipped":     False,
    "tts_voice_label":  "Sun-Hi — Weiblich (Seoul)",
    "tts_speed_label":  "📖 Lerntempo",
}.items():
    st.session_state.setdefault(k, v)

# ── CSS — mobile-first + dark ────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Pretendard', 'Noto Sans KR', sans-serif;
    -webkit-tap-highlight-color: transparent;
    -webkit-font-smoothing: antialiased;
}
.block-container {
    padding: .8rem .9rem 2rem .9rem !important;
    max-width: 720px !important;
}
@supports (padding: max(0px)) {
    .block-container {
        padding-bottom: max(2rem, env(safe-area-inset-bottom)) !important;
    }
}

.back-link {
    font-size: .8rem; color: #495057; text-decoration: none !important;
    display: inline-block; padding: 4px 0; margin-bottom: .4rem;
}
.page-title {
    font-size: 1.3rem; font-weight: 800; margin: 0 0 .15rem; letter-spacing: -.01em;
    color: #7d4a00;
}
.page-sub { font-size: .8rem; color: #868e96; margin: 0 0 .8rem; }

.chips { display: flex; gap: 6px; flex-wrap: wrap; margin: .4rem 0 .8rem; }
.chip {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 4px 10px; border-radius: 100px;
    background: #f1f3f5; color: #495057;
    font-size: .75rem; font-weight: 600;
}
.chip.warning { background: #fff9db; color: #7d4a00; }
.chip.accent  { background: #fff0f6; color: #c2255c; }

/* Flip overlay */
[data-testid="stVerticalBlock"]:has(.gfc-front),
[data-testid="stVerticalBlock"]:has(.gfc-back) {
    position: relative !important;
}
[data-testid="stVerticalBlock"]:has(.gfc-front) [data-testid="stForm"],
[data-testid="stVerticalBlock"]:has(.gfc-back)  [data-testid="stForm"] {
    position: absolute !important; top: 0 !important; left: 0 !important;
    right: 0 !important; height: 100% !important; border: none !important;
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
    height: 280px !important; cursor: pointer !important;
    background: transparent !important;
}

[data-testid="stHorizontalBlock"]:has(.gfc-front) [data-testid="stColumn"]:first-child button,
[data-testid="stHorizontalBlock"]:has(.gfc-back)  [data-testid="stColumn"]:first-child button,
[data-testid="stHorizontalBlock"]:has(.gfc-front) [data-testid="stColumn"]:last-child button,
[data-testid="stHorizontalBlock"]:has(.gfc-back)  [data-testid="stColumn"]:last-child button {
    font-size: 1.6rem !important; height: 280px !important;
    background: transparent !important; border: none !important;
    color: #adb5bd !important; transition: color .15s, transform .12s;
}
[data-testid="stHorizontalBlock"]:has(.gfc-front) [data-testid="stColumn"]:first-child button:active,
[data-testid="stHorizontalBlock"]:has(.gfc-back)  [data-testid="stColumn"]:first-child button:active,
[data-testid="stHorizontalBlock"]:has(.gfc-front) [data-testid="stColumn"]:last-child button:active,
[data-testid="stHorizontalBlock"]:has(.gfc-back)  [data-testid="stColumn"]:last-child button:active {
    color: #f59f00 !important; transform: scale(.92);
}

.gfc-front, .gfc-back {
    border-radius: 18px; padding: 1.4rem 1.2rem;
    height: 280px;
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; text-align: center; user-select: none;
    box-sizing: border-box;
    transition: transform .2s ease;
}
.gfc-front {
    background: linear-gradient(135deg, #fffaeb, #ffec99);
    border: 2px solid #f59f00;
    box-shadow: 0 4px 16px rgba(245, 159, 0, .15);
}
.gfc-back {
    background: linear-gradient(135deg, #fff5f9, #fce4ec);
    border: 2px solid #e64980;
    box-shadow: 0 4px 16px rgba(230, 73, 128, .15);
}
.gfc-level {
    font-size: .68rem; font-weight: 800; color: #fff;
    background: #f59f00; border-radius: 100px;
    padding: 3px 10px; margin-bottom: .5rem; letter-spacing: .04em;
}
.gfc-back .gfc-level { background: #e64980; }
.gfc-pattern    { font-size: 1.55rem; font-weight: 800; color: #7d4a00; margin: 0 0 .3rem; line-height: 1.2; }
.gfc-type       { font-size: .82rem; color: #e67700; font-weight: 700; margin-bottom: .3rem; }
.gfc-explanation{ font-size: .95rem; color: #495057; line-height: 1.55; margin-bottom: .6rem; }
.gfc-example    { font-size: 1rem; color: #880e4f; font-weight: 700; margin-bottom: .2rem; line-height: 1.35; }
.gfc-german     { font-size: .88rem; color: #495057; font-style: italic; margin-bottom: .35rem; line-height: 1.4; }
.gfc-note       { font-size: .76rem; color: #868e96; border-top: 1px solid #f8bbd0; padding-top: .35rem; margin-top: .15rem; line-height: 1.4; }
.gfc-hint       { font-size: .78rem; color: #868e96; margin-top: .8rem; opacity: .8; }

.stButton > button {
    width: 100%; min-height: 44px;
    border-radius: 12px; font-weight: 600;
}

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; height: 0; }

@media (max-width: 480px) {
    .block-container { padding-left: .65rem !important; padding-right: .65rem !important; }
    .gfc-front, .gfc-back { padding: 1.1rem .85rem; height: 260px; }
    [data-testid="stVerticalBlock"]:has(.gfc-front) [data-testid="stForm"] button,
    [data-testid="stVerticalBlock"]:has(.gfc-back)  [data-testid="stForm"] button { height: 260px !important; }
    [data-testid="stHorizontalBlock"]:has(.gfc-front) [data-testid="stColumn"]:first-child button,
    [data-testid="stHorizontalBlock"]:has(.gfc-back)  [data-testid="stColumn"]:first-child button,
    [data-testid="stHorizontalBlock"]:has(.gfc-front) [data-testid="stColumn"]:last-child button,
    [data-testid="stHorizontalBlock"]:has(.gfc-back)  [data-testid="stColumn"]:last-child button { height: 260px !important; }
    .gfc-pattern { font-size: 1.35rem; }
    .gfc-explanation { font-size: .88rem; }
    .gfc-example { font-size: .92rem; }
}

@media (prefers-color-scheme: dark) {
    .back-link { color: #adb5bd; }
    .page-title { color: #ffd43b; }
    .page-sub { color: #6c757d; }
    .chip { background: #2a2f36; color: #ced4da; }
    .chip.warning { background: #3a3017; color: #ffd43b; }
    .chip.accent  { background: #3a1a2c; color: #fcc2d7; }
    .gfc-front {
        background: linear-gradient(135deg, #3a2e0e, #2e2616);
        border-color: #f59f00;
    }
    .gfc-back {
        background: linear-gradient(135deg, #2a1525, #3a1a2c);
        border-color: #e64980;
    }
    .gfc-pattern { color: #ffd43b; }
    .gfc-type { color: #ffa94d; }
    .gfc-explanation { color: #ced4da; }
    .gfc-example { color: #fcc2d7; }
    .gfc-german { color: #adb5bd; }
    .gfc-note { color: #868e96; border-top-color: #4a2a3e; }
    .gfc-hint { color: #6c757d; }
}
</style>
""", unsafe_allow_html=True)

# ── User gate ─────────────────────────────────────────────────────────────────
user = require_user()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<a class="back-link" href="/" target="_self">← Zurück</a>', unsafe_allow_html=True)
st.markdown('<h1 class="page-title">📝 문법 · Grammatik</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="page-sub">Hi {user["name"]} · Tippe für Erklärung + Beispiel</p>', unsafe_allow_html=True)

# ── Daten + Filter ────────────────────────────────────────────────────────────
df_all = load_grammar()

with st.expander("🔍 Filter", expanded=False):
    fc1, fc2 = st.columns(2)
    sel_level = fc1.selectbox("Level", ["Alle"] + sorted(df_all["level"].unique().tolist()), key="gr_f_level")
    sel_type  = fc2.selectbox("Typ",   ["Alle"] + sorted(df_all["type_de"].unique().tolist()), key="gr_f_type")

# ── Sidebar — TTS ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔊 Aussprache")
    voice_label = st.selectbox(
        "Stimme", list(VOICES.keys()),
        index=list(VOICES.keys()).index(st.session_state.tts_voice_label),
    )
    speed_label = st.selectbox(
        "Tempo", list(SPEED_PRESETS.keys()),
        index=list(SPEED_PRESETS.keys()).index(st.session_state.tts_speed_label),
    )
    st.session_state.tts_voice_label = voice_label
    st.session_state.tts_speed_label = speed_label
    voice = VOICES[voice_label]
    speed = f"{SPEED_PRESETS[speed_label]:+d}%"

    st.divider()
    st.markdown(
        "**💡 Lerntipp**\n\n"
        "1. Vorderseite = Grammatikmuster\n"
        "2. Selber überlegen\n"
        "3. Karte umdrehen für Erklärung\n"
    )

# ── Filter anwenden ───────────────────────────────────────────────────────────
df = df_all.copy()
if sel_level != "Alle":
    df = df[df["level"] == sel_level]
if sel_type != "Alle":
    df = df[df["type_de"] == sel_type]
df = df.reset_index(drop=True)

if df.empty:
    st.warning("Keine Grammatik für diesen Filter.")
    st.stop()

idx = st.session_state.gram_idx % len(df)
st.session_state.gram_idx = idx
row = df.iloc[idx]

# ── Stats ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="chips">
    <span class="chip warning">📝 {idx+1} / {len(df)}</span>
    <span class="chip">Level: {row.level}</span>
    <span class="chip accent">{row.type_de}</span>
</div>
""", unsafe_allow_html=True)

# ── Tabs: Karten + Levels ────────────────────────────────────────────────────
tab_card, tab_a1, tab_a2, tab_b1, tab_b2 = st.tabs(["🃏 Karte", "A1", "A2", "B1", "B2"])

with tab_card:
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
        if st.button("🔊 Beispiel hören", use_container_width=True):
            with st.spinner("Lade Audio…"):
                audio = get_cached_audio(row.example_korean, voice, speed)
                st.markdown(audio_html(audio), unsafe_allow_html=True)

    # Bottom nav
    st.markdown("")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("⏮ Erste", use_container_width=True, key="gram_first"):
            st.session_state.gram_idx = 0
            st.session_state.gram_flipped = False
            st.rerun()
    with b2:
        if st.button("🔀 Zufällig", use_container_width=True, key="gram_rand"):
            st.session_state.gram_idx = random.randint(0, len(df) - 1)
            st.session_state.gram_flipped = False
            st.rerun()
    with b3:
        if st.button("⏭ Letzte", use_container_width=True, key="gram_last"):
            st.session_state.gram_idx = len(df) - 1
            st.session_state.gram_flipped = False
            st.rerun()

# ── Level-Tabs ────────────────────────────────────────────────────────────────
for tab, lvl in zip([tab_a1, tab_a2, tab_b1, tab_b2], ["A1", "A2", "B1", "B2"]):
    with tab:
        subset = df_all[df_all["level"] == lvl][
            ["pattern", "type_de", "explanation_de", "example_korean", "example_german"]
        ]
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
