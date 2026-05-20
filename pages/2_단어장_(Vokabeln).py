"""📚 단어장 — Koreanische Vokabelkarten (A1→B2)"""
import random
import sys, pathlib
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from lib.tts import VOICES, SPEED_PRESETS, get_cached_audio, audio_html
from lib.data import load_vocab

st.set_page_config(
    page_title="📚 단어장",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Session State ─────────────────────────────────────────────────────────────
_DEF = {
    "vok_idx":         0,
    "vok_flipped":     False,
    "vok_correct":     0,
    "vok_skipped":     0,
    "vok_seen_ids":    [],
    "tts_voice_label": "Sun-Hi — Weiblich (Seoul)",
    "tts_speed_label": "📖 Lerntempo",
}
for k, v in _DEF.items():
    st.session_state.setdefault(k, v)

# ── CSS — mobile-first + dark mode ───────────────────────────────────────────
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

/* ── Header ─────────────────────────────────────────────── */
.back-link {
    font-size: .8rem; color: #495057; text-decoration: none !important;
    display: inline-block; padding: 4px 0; margin-bottom: .4rem;
}
.page-title {
    font-size: 1.3rem; font-weight: 800; margin: 0 0 .15rem; letter-spacing: -.01em;
    color: #1864ab;
}
.page-sub { font-size: .8rem; color: #868e96; margin: 0 0 .8rem; }

/* ── Chip row (stats) ───────────────────────────────────── */
.chips { display: flex; gap: 6px; flex-wrap: wrap; margin: .4rem 0 .8rem; }
.chip {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 4px 10px; border-radius: 100px;
    background: #f1f3f5; color: #495057;
    font-size: .75rem; font-weight: 600;
}
.chip.primary { background: #e7f5ff; color: #1864ab; }
.chip.success { background: #ebfbee; color: #2b8a3e; }
.chip.warning { background: #fff9db; color: #7d4a00; }

/* ── Progress ─────────────────────────────────────────── */
.prog-bar  { height: 5px; border-radius: 3px; background: #dee2e6; margin: .35rem 0 .8rem; overflow: hidden; }
.prog-fill { height: 100%; background: linear-gradient(90deg, #339af0, #51cf66); transition: width .3s ease; }

/* ── Card (flip overlay) ─────────────────────────────── */
[data-testid="stVerticalBlock"]:has(.fc-front),
[data-testid="stVerticalBlock"]:has(.fc-back) {
    position: relative !important;
}
[data-testid="stVerticalBlock"]:has(.fc-front) [data-testid="stForm"],
[data-testid="stVerticalBlock"]:has(.fc-back)  [data-testid="stForm"] {
    position: absolute !important; top: 0 !important; left: 0 !important;
    right: 0 !important; height: 100% !important; border: none !important;
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

.fc-front, .fc-back {
    border-radius: 18px; padding: 1.4rem 1.2rem;
    height: 220px;
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; text-align: center; user-select: none;
    box-sizing: border-box;
    box-shadow: 0 4px 16px rgba(51, 154, 240, .12);
    transition: transform .2s ease;
}
.fc-front {
    background: linear-gradient(135deg, #e7f5ff, #d0ebff);
    border: 2px solid #339af0;
}
.fc-back {
    background: linear-gradient(135deg, #ebfbee, #d3f9d8);
    border: 2px solid #51cf66;
    box-shadow: 0 4px 16px rgba(81, 207, 102, .15);
}
.fc-level {
    font-size: .68rem; font-weight: 800; color: #fff;
    background: rgba(255,255,255,.25); border-radius: 100px;
    padding: 3px 10px; margin-bottom: .5rem;
    letter-spacing: .04em;
}
.fc-front .fc-level { background: #339af0; }
.fc-back  .fc-level { background: #51cf66; }
.fc-korean   { font-size: 2.4rem; font-weight: 800; color: #1864ab; margin: 0 0 .25rem; line-height: 1.15; }
.fc-roman    { font-size: 1rem; color: #4c9fd6; margin-bottom: .4rem; font-style: italic; }
.fc-german   { font-size: 1.6rem; font-weight: 800; color: #2b8a3e; margin: 0 0 .25rem; line-height: 1.2; }
.fc-pos      { font-size: .78rem; color: #868e96; margin-bottom: .15rem; }
.fc-example  { font-size: .85rem; color: #495057; margin-top: .5rem; line-height: 1.5; }
.fc-example em { font-weight: 600; font-style: normal; color: #1864ab; }
.fc-back .fc-example em { color: #2b8a3e; }
.fc-hint     { font-size: .75rem; color: #868e96; margin-top: .5rem; opacity: .7; }

/* ── Nav arrows ───────────────────────────────────────── */
[data-testid="stHorizontalBlock"]:has(.fc-front) [data-testid="stColumn"]:first-child button,
[data-testid="stHorizontalBlock"]:has(.fc-back)  [data-testid="stColumn"]:first-child button,
[data-testid="stHorizontalBlock"]:has(.fc-front) [data-testid="stColumn"]:last-child button,
[data-testid="stHorizontalBlock"]:has(.fc-back)  [data-testid="stColumn"]:last-child button {
    font-size: 1.6rem !important; height: 220px !important;
    background: transparent !important; border: none !important;
    color: #adb5bd !important; transition: color .15s, transform .12s;
}
[data-testid="stHorizontalBlock"]:has(.fc-front) [data-testid="stColumn"]:first-child button:active,
[data-testid="stHorizontalBlock"]:has(.fc-back)  [data-testid="stColumn"]:first-child button:active,
[data-testid="stHorizontalBlock"]:has(.fc-front) [data-testid="stColumn"]:last-child button:active,
[data-testid="stHorizontalBlock"]:has(.fc-back)  [data-testid="stColumn"]:last-child button:active {
    color: #339af0 !important; transform: scale(.92);
}

/* ── Streamlit buttons (mobile) ──────────────────────────── */
.stButton > button {
    width: 100%; min-height: 44px;
    border-radius: 12px; font-weight: 600;
}

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; height: 0; }

/* ── Action buttons after flip — make them obvious */
.action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem; margin-top: .5rem; }

/* ── Smaller screens ──────────────────────────────────── */
@media (max-width: 480px) {
    .block-container { padding-left: .65rem !important; padding-right: .65rem !important; }
    .fc-front, .fc-back { padding: 1.2rem .9rem; height: 200px; }
    [data-testid="stVerticalBlock"]:has(.fc-front) [data-testid="stForm"] button,
    [data-testid="stVerticalBlock"]:has(.fc-back)  [data-testid="stForm"] button { height: 200px !important; }
    [data-testid="stHorizontalBlock"]:has(.fc-front) [data-testid="stColumn"]:first-child button,
    [data-testid="stHorizontalBlock"]:has(.fc-back)  [data-testid="stColumn"]:first-child button,
    [data-testid="stHorizontalBlock"]:has(.fc-front) [data-testid="stColumn"]:last-child button,
    [data-testid="stHorizontalBlock"]:has(.fc-back)  [data-testid="stColumn"]:last-child button { height: 200px !important; }
    .fc-korean { font-size: 2rem; }
    .fc-german { font-size: 1.4rem; }
    .fc-example { font-size: .82rem; }
}

/* ── Dark mode ────────────────────────────────────────── */
@media (prefers-color-scheme: dark) {
    .back-link { color: #adb5bd; }
    .page-title { color: #74c0fc; }
    .page-sub { color: #6c757d; }
    .chip { background: #2a2f36; color: #ced4da; }
    .chip.primary { background: #1d3557; color: #74c0fc; }
    .chip.success { background: #1b3a23; color: #8ce99a; }
    .chip.warning { background: #3a3017; color: #ffd43b; }
    .prog-bar { background: #2a2f36; }
    .fc-front {
        background: linear-gradient(135deg, #0f2942, #162e4d);
        border-color: #339af0;
    }
    .fc-back {
        background: linear-gradient(135deg, #0f2a1a, #15321e);
        border-color: #51cf66;
    }
    .fc-korean { color: #a5d8ff; }
    .fc-roman { color: #74c0fc; }
    .fc-german { color: #b2f2bb; }
    .fc-pos, .fc-hint { color: #6c757d; }
    .fc-example { color: #ced4da; }
    .fc-example em { color: #a5d8ff; }
    .fc-back .fc-example em { color: #b2f2bb; }
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<a class="back-link" href="/" target="_self">← Zurück</a>', unsafe_allow_html=True)
st.markdown('<h1 class="page-title">📚 단어장 · Vokabeln</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Tippe auf die Karte · Wische ◀ ▶ zum Blättern</p>', unsafe_allow_html=True)

# ── Daten + Filter ────────────────────────────────────────────────────────────
df_all = load_vocab()

with st.expander("🔍 Filter & Kartenrichtung", expanded=False):
    fc1, fc2 = st.columns(2)
    sel_level = fc1.selectbox("Level",   ["Alle"] + sorted(df_all["level"].unique().tolist()),  key="vok_f_level")
    sel_pos   = fc2.selectbox("Wortart", ["Alle"] + sorted(df_all["pos_de"].unique().tolist()), key="vok_f_pos")
    sel_topic = st.selectbox("Thema",    ["Alle"] + sorted(df_all["topic"].unique().tolist()),  key="vok_f_topic")
    direction = st.radio(
        "Vorderseite zeigt",
        ["🇰🇷 Koreanisch → 🇩🇪 Deutsch", "🇩🇪 Deutsch → 🇰🇷 Koreanisch"],
        key="vok_dir",
    )

# ── Sidebar — TTS Einstellungen ──────────────────────────────────────────────
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
    if st.button("🔄 Session zurücksetzen", use_container_width=True):
        st.session_state.vok_correct = 0
        st.session_state.vok_skipped = 0
        st.session_state.vok_seen_ids = []
        st.session_state.vok_idx = 0
        st.session_state.vok_flipped = False
        st.rerun()

# ── Filter anwenden ───────────────────────────────────────────────────────────
df = df_all.copy()
if sel_level != "Alle":
    df = df[df["level"] == sel_level]
if sel_topic != "Alle":
    df = df[df["topic"] == sel_topic]
if sel_pos != "Alle":
    df = df[df["pos_de"] == sel_pos]
df = df.reset_index(drop=True)

if df.empty:
    st.warning("Keine Vokabeln für diesen Filter. Passe oben die Auswahl an.")
    st.stop()

idx = st.session_state.vok_idx % len(df)
st.session_state.vok_idx = idx
row = df.iloc[idx]

# ── Stat chips + progress ────────────────────────────────────────────────────
seen = len(set(st.session_state.vok_seen_ids))
pct  = seen / max(1, len(df_all)) * 100

st.markdown(f"""
<div class="chips">
    <span class="chip primary">📚 {idx+1} / {len(df)}</span>
    <span class="chip">📊 {seen} entdeckt</span>
    <span class="chip success">✅ {st.session_state.vok_correct}</span>
    <span class="chip warning">⏭ {st.session_state.vok_skipped}</span>
</div>
<div class="prog-bar"><div class="prog-fill" style="width:{pct:.0f}%"></div></div>
""", unsafe_allow_html=True)

# ── Karte ─────────────────────────────────────────────────────────────────────
flipped  = st.session_state.vok_flipped
ko_first = "Koreanisch →" in direction

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
        <div class="fc-example"><em>{row.example_korean}</em><br>{row.example_german}</div>
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
        <div class="fc-example"><em>{row.example_korean}</em><br>{row.example_german}</div>
    </div>"""

card_html = back_html if flipped else front_html

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
                    st.session_state.cards_flipped    = st.session_state.get("cards_flipped",    0) + 1
            st.rerun()

with _next_col:
    if st.button("▶", key="nav_next"):
        st.session_state.vok_idx = (idx + 1) % len(df)
        st.session_state.vok_flipped = False
        st.rerun()

# ── TTS + Antwort-Buttons ────────────────────────────────────────────────────
if st.button("🔊 Aussprache hören", use_container_width=True, key="tts_btn"):
    with st.spinner("Lade Audio…"):
        audio = get_cached_audio(row.korean, voice, speed)
        st.markdown(audio_html(audio), unsafe_allow_html=True)

if flipped:
    ac1, ac2 = st.columns(2)
    with ac1:
        if st.button("✅ Gewusst!", use_container_width=True, key="correct_btn", type="primary"):
            st.session_state.vok_correct += 1
            st.session_state.correct_answers = st.session_state.get("correct_answers", 0) + 1
            st.session_state.vok_idx = (idx + 1) % len(df)
            st.session_state.vok_flipped = False
            st.rerun()
    with ac2:
        if st.button("⏭ Überspringen", use_container_width=True, key="skip_btn"):
            st.session_state.vok_skipped += 1
            st.session_state.vok_idx = (idx + 1) % len(df)
            st.session_state.vok_flipped = False
            st.rerun()

# ── Bottom-Navigation ────────────────────────────────────────────────────────
st.markdown("")
b1, b2, b3 = st.columns(3)
with b1:
    if st.button("⏮ Erste", use_container_width=True):
        st.session_state.vok_idx = 0
        st.session_state.vok_flipped = False
        st.rerun()
with b2:
    if st.button("🔀 Zufällig", use_container_width=True):
        st.session_state.vok_idx = random.randint(0, len(df) - 1)
        st.session_state.vok_flipped = False
        st.rerun()
with b3:
    if st.button("⏭ Letzte", use_container_width=True):
        st.session_state.vok_idx = len(df) - 1
        st.session_state.vok_flipped = False
        st.rerun()

# ── Swipe-Gesten ──────────────────────────────────────────────────────────────
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
            if (btns[i].textContent.trim() === label) { btns[i].click(); break; }
        }
    }, {passive:true});
})();
</script>
""", height=0)

# ── Vokabelliste ──────────────────────────────────────────────────────────────
with st.expander("📋 Alle Vokabeln dieser Auswahl"):
    show_df = df[["korean", "romanization", "german", "level", "pos_de", "topic"]].copy()
    show_df.columns = ["Koreanisch", "Romanisierung", "Deutsch", "Level", "Wortart", "Thema"]
    st.dataframe(show_df, use_container_width=True, hide_index=True)
