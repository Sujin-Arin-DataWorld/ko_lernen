"""🇰🇷 Koreanisch lernen — Persönlicher Trainer"""
import streamlit as st

st.set_page_config(
    page_title="🇰🇷 Koreanisch lernen",
    page_icon="🇰🇷",
    layout="centered",
    initial_sidebar_state="collapsed",
)

_DEFAULTS = {
    "total_cards_seen":  0,
    "cards_flipped":     0,
    "correct_answers":   0,
    "tts_cache":         {},
    "tts_voice_label":   "Sun-Hi — Weiblich (Seoul)",
    "tts_speed_label":   "📖 Lerntempo",
    "current_level_idx": 0,
}
for k, v in _DEFAULTS.items():
    st.session_state.setdefault(k, v)

LEVELS  = ["A1.1", "A1.2", "A2.1", "A2.2", "B1.1", "B1.2", "B2.1", "B2"]
current = st.session_state.current_level_idx

# ── Mobile-first CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Pretendard', 'Noto Sans KR', sans-serif;
    -webkit-tap-highlight-color: transparent;
    -webkit-font-smoothing: antialiased;
}
.block-container {
    padding: 1rem .9rem 2rem .9rem !important;
    max-width: 720px !important;
}
@supports (padding: max(0px)) {
    .block-container {
        padding-bottom: max(2rem, env(safe-area-inset-bottom)) !important;
    }
}

/* ── Hero ─────────────────────────────────────────────────────────────── */
.hero-title {
    font-size: 1.55rem; font-weight: 800; margin: 0 0 .15rem; letter-spacing: -.01em;
    background: linear-gradient(135deg, #e64980 0%, #845ef7 60%, #339af0 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub  { font-size: .92rem; color: #6c757d; margin: 0 0 .15rem; font-weight: 500; }
.hero-meta { font-size: .75rem; color: #adb5bd; }

/* ── Featured (today's pick) ──────────────────────────────────────────── */
.featured {
    display: block; text-decoration: none !important;
    border-radius: 16px; padding: 1.1rem 1.2rem; margin: 1rem 0 .8rem;
    background: linear-gradient(135deg, #845ef7 0%, #5f3dc4 100%);
    box-shadow: 0 6px 20px rgba(132, 94, 247, .25);
    transition: transform .15s ease, box-shadow .15s ease;
}
.featured:active { transform: scale(.985); box-shadow: 0 3px 10px rgba(132, 94, 247, .35); }
.featured * { color: #fff !important; text-decoration: none !important; }
.feat-label {
    font-size: .68rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; opacity: .85; margin: 0 0 .35rem;
}
.feat-title { font-size: 1.15rem; font-weight: 700; margin: 0 0 .25rem; display: flex; align-items: center; gap: .4rem; }
.feat-desc  { font-size: .85rem; opacity: .9; margin: 0; line-height: 1.4; }
.feat-cta   { font-size: .8rem; opacity: .85; margin-top: .6rem; display: inline-block; }

/* ── Stat chips ──────────────────────────────────────────────────────── */
.chips { display: flex; gap: 6px; flex-wrap: wrap; margin: .5rem 0 1rem; }
.chip {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 5px 11px; border-radius: 100px;
    background: #f1f3f5; color: #495057;
    font-size: .78rem; font-weight: 600;
}
.chip.primary { background: #e7f5ff; color: #1864ab; }
.chip.success { background: #ebfbee; color: #2b8a3e; }
.chip.warning { background: #fff9db; color: #7d4a00; }
.chip.accent  { background: #f3f0ff; color: #5f3dc4; }

/* ── Section heading ─────────────────────────────────────────────────── */
.section-h {
    font-size: .85rem; font-weight: 700; margin: 1.2rem 0 .6rem;
    color: #495057; letter-spacing: -.005em;
    display: flex; align-items: center; justify-content: space-between;
}
.section-h .sh-aside { font-size: .72rem; color: #adb5bd; font-weight: 500; }

/* ── Level pip grid (8 columns, single row, HTML links) ───────────────── */
.lvl-grid {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 6px;
    margin: .5rem 0 .8rem;
}
.lvl-pip {
    display: flex; flex-direction: column;
    align-items: center; gap: 5px;
    text-decoration: none !important;
    color: inherit !important;
    transition: transform .12s ease;
    -webkit-tap-highlight-color: transparent;
}
.lvl-pip:active { transform: scale(.9); }
.lvl-pip-mark {
    width: 100%; aspect-ratio: 1;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: .82rem;
    background: #f1f3f5; color: #adb5bd;
    border: 2px solid transparent;
    line-height: 1;
}
.lvl-pip.done    .lvl-pip-mark { background: #d3f9d8; color: #2b8a3e; }
.lvl-pip.current .lvl-pip-mark {
    background: #e5dbff; color: #5f3dc4; border-color: #845ef7;
    box-shadow: 0 4px 12px rgba(132,94,247,.3);
}
.lvl-pip-lbl {
    font-size: .62rem; font-weight: 700;
    color: #adb5bd; letter-spacing: -.03em;
    text-align: center; line-height: 1;
    white-space: nowrap;
}
.lvl-pip.done    .lvl-pip-lbl { color: #2b8a3e; }
.lvl-pip.current .lvl-pip-lbl { color: #5f3dc4; }

/* ── Module cards ────────────────────────────────────────────────────── */
.modules { display: grid; gap: .65rem; }
.mod-card {
    display: block; text-decoration: none !important;
    border-radius: 14px; padding: .95rem 1.1rem;
    border: 1.5px solid; min-height: 72px;
    transition: transform .12s ease, box-shadow .15s ease;
    position: relative;
}
.mod-card:active { transform: scale(.985); }
.mod-card * { text-decoration: none !important; }
.mod-card .mod-title {
    font-size: .98rem; font-weight: 700; margin: 0 0 .2rem;
    display: flex; align-items: center; gap: .5rem;
}
.mod-card .mod-desc { font-size: .8rem; margin: 0; opacity: .8; line-height: 1.45; }
.mod-card .mod-arrow {
    position: absolute; right: 1rem; top: 50%; transform: translateY(-50%);
    opacity: .55; font-size: 1.2rem;
}
.mod-hangul  { border-color: #e64980; background: linear-gradient(135deg,#fff5f9,#fce4ec); color: #880e4f; }
.mod-vocab   { border-color: #339af0; background: linear-gradient(135deg,#f0f7ff,#d0ebff); color: #1864ab; }
.mod-grammar { border-color: #f59f00; background: linear-gradient(135deg,#fffaeb,#ffec99); color: #7d4a00; }
.mod-listen  { border-color: #51cf66; background: linear-gradient(135deg,#f1fff3,#d3f9d8); color: #2b8a3e; }

/* ── Streamlit button defaults (mobile-friendly) ─────────────────────── */
.stButton > button {
    width: 100%; min-height: 44px;
    border-radius: 12px; font-weight: 600;
}
[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, #845ef7, #5f3dc4) !important;
}

/* Hide Streamlit chrome (keep header for sidebar toggle) */
#MainMenu, footer { visibility: hidden; height: 0; }

/* ── Footer ──────────────────────────────────────────────────────────── */
.footer {
    font-size: .72rem; color: #adb5bd; text-align: center;
    margin-top: 1.5rem; padding-top: .8rem; border-top: 1px solid #f1f3f5;
}

/* ── Smaller screens ─────────────────────────────────────────────────── */
@media (max-width: 480px) {
    .block-container { padding-left: .7rem !important; padding-right: .7rem !important; }
    .hero-title { font-size: 1.35rem; }
    .featured { padding: .95rem 1rem; }
    .feat-title { font-size: 1.05rem; }
    .feat-desc { font-size: .8rem; }
    .mod-card { padding: .85rem 1rem; }
    .mod-card .mod-title { font-size: .92rem; }
    .mod-card .mod-desc { font-size: .76rem; }
    .lvl-grid { gap: 4px; }
    .lvl-pip-mark { font-size: .72rem; }
    .lvl-pip-lbl { font-size: .56rem; }
}

/* ── Dark mode ───────────────────────────────────────────────────────── */
@media (prefers-color-scheme: dark) {
    .hero-sub { color: #adb5bd; }
    .hero-meta { color: #6c757d; }
    .section-h { color: #ced4da; }
    .section-h .sh-aside { color: #6c757d; }
    .chip { background: #2a2f36; color: #ced4da; }
    .chip.primary { background: #1d3557; color: #74c0fc; }
    .chip.success { background: #1b3a23; color: #8ce99a; }
    .chip.warning { background: #3a3017; color: #ffd43b; }
    .chip.accent  { background: #3b2c66; color: #d0bfff; }
    .lvl-pip-mark { background: #2a2f36; color: #6c757d; }
    .lvl-pip.done    .lvl-pip-mark { background: #1b3a23; color: #8ce99a; }
    .lvl-pip.current .lvl-pip-mark { background: #3b2c66; color: #d0bfff; border-color: #845ef7; }
    .lvl-pip-lbl { color: #6c757d; }
    .lvl-pip.done    .lvl-pip-lbl { color: #8ce99a; }
    .lvl-pip.current .lvl-pip-lbl { color: #d0bfff; }
    .mod-hangul  { background: linear-gradient(135deg,#2a1525,#3a1a2c); color: #fcc2d7; border-color: #d6336c; }
    .mod-vocab   { background: linear-gradient(135deg,#0f2942,#162e4d); color: #a5d8ff; border-color: #339af0; }
    .mod-grammar { background: linear-gradient(135deg,#3a2e0e,#2e2616); color: #ffe066; border-color: #f59f00; }
    .mod-listen  { background: linear-gradient(135deg,#0f2a1a,#15321e); color: #b2f2bb; border-color: #51cf66; }
    .footer { color: #6c757d; border-top-color: #2a2f36; }
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="hero-title">🇰🇷 한국어 — Koreanisch</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">안녕하세요! 오늘도 화이팅 💪</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="hero-meta">Persönlicher Trainer · Level <b>{LEVELS[current]}</b></p>',
    unsafe_allow_html=True,
)

# ── Featured pick ─────────────────────────────────────────────────────────────
PICKS = [
    ("📚", "Vokabeln auffrischen", "Beginne mit A1-Grundwortschatz · 500+ Karten warten",          "/단어장_(Vokabeln)"),
    ("🔤", "Hangul festigen",       "Lies und schreibe das koreanische Alphabet sicher",            "/한글연습_(Hangul)"),
    ("📝", "Grammatik vertiefen",   "Strukturen verstehen statt auswendig lernen",                  "/문법카드_(Grammatik)"),
    ("🎧", "Hör-Training",          "Mit echten Sätzen das Ohr trainieren",                         "/듣기연습_(Hören)"),
]
emoji, ftitle, fdesc, fhref = PICKS[min(current, len(PICKS) - 1)]
st.markdown(f"""
<a href="{fhref}" target="_self" class="featured">
    <div class="feat-label">🎯 Heute empfohlen</div>
    <div class="feat-title">{emoji} {ftitle}</div>
    <div class="feat-desc">{fdesc}</div>
    <div class="feat-cta">Jetzt starten →</div>
</a>
""", unsafe_allow_html=True)

# ── Stat chips ────────────────────────────────────────────────────────────────
seen    = st.session_state.total_cards_seen
flipped = st.session_state.cards_flipped
correct = st.session_state.correct_answers
acc     = int(correct / max(1, seen) * 100)

st.markdown(f"""
<div class="chips">
    <span class="chip primary">📊 {seen} gesehen</span>
    <span class="chip">🔄 {flipped} umgedreht</span>
    <span class="chip success">✅ {correct} richtig</span>
    <span class="chip warning">🎯 {acc}%</span>
</div>
""", unsafe_allow_html=True)

# ── Level Progress ────────────────────────────────────────────────────────────
# URL-Klick auf Level-Pip auswerten (?set_lvl=N)
_set_lvl = st.query_params.get("set_lvl")
if _set_lvl is not None:
    try:
        _new = int(_set_lvl)
        if 0 <= _new < len(LEVELS):
            st.session_state.current_level_idx = _new
    except (ValueError, TypeError):
        pass
    if "set_lvl" in st.query_params:
        del st.query_params["set_lvl"]
    st.rerun()

current = st.session_state.current_level_idx  # nach evt. Update

st.markdown(
    '<div class="section-h">📈 Dein Level <span class="sh-aside">Tippen zum Setzen</span></div>',
    unsafe_allow_html=True,
)

# Pip-Grid (HTML <a>-Links, kein Streamlit-Button) — keine :has-Abhängigkeit
from urllib.parse import urlencode
_keep_q = {k: v for k in ("name", "os") if (v := st.query_params.get(k))}

def _pip_href(i: int) -> str:
    return "?" + urlencode({**_keep_q, "set_lvl": i})

_pips = []
for i, lvl in enumerate(LEVELS):
    if i < current:
        cls, mark = "done", "✓"
    elif i == current:
        cls, mark = "current", "📍"
    else:
        cls, mark = "todo", "·"
    _pips.append(
        f'<a class="lvl-pip {cls}" href="{_pip_href(i)}" target="_self" title="Auf {lvl} setzen">'
        f'<span class="lvl-pip-mark">{mark}</span>'
        f'<span class="lvl-pip-lbl">{lvl}</span></a>'
    )
st.markdown(f'<div class="lvl-grid">{"".join(_pips)}</div>', unsafe_allow_html=True)
st.progress((current + 0.5) / len(LEVELS))

# ── Modules ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-h">🎯 Lernmodule</div>', unsafe_allow_html=True)
st.markdown("""
<div class="modules">
<a href="/한글연습_(Hangul)" target="_self" class="mod-card mod-hangul">
    <div class="mod-title">🔤 한글 · Hangul</div>
    <p class="mod-desc">Konsonanten · Vokale · Silben · 24 Grundzeichen</p>
    <span class="mod-arrow">›</span>
</a>
<a href="/단어장_(Vokabeln)" target="_self" class="mod-card mod-vocab">
    <div class="mod-title">📚 단어장 · Vokabeln</div>
    <p class="mod-desc">500+ Karten · A1→B2 · TTS-Aussprache · Wische zum Blättern</p>
    <span class="mod-arrow">›</span>
</a>
<a href="/문법카드_(Grammatik)" target="_self" class="mod-card mod-grammar">
    <div class="mod-title">📝 문법 · Grammatik</div>
    <p class="mod-desc">85+ Muster · Erklärung auf Deutsch · Beispielsätze</p>
    <span class="mod-arrow">›</span>
</a>
<a href="/듣기연습_(Hören)" target="_self" class="mod-card mod-listen">
    <div class="mod-title">🎧 듣기 · Hören</div>
    <p class="mod-desc">Sätze hören · Diktat-Modus · Geschwindigkeit anpassbar</p>
    <span class="mod-arrow">›</span>
</a>
</div>
""", unsafe_allow_html=True)

# ── Tip ───────────────────────────────────────────────────────────────────────
with st.expander("💡 Lerntipp des Tages"):
    st.markdown(
        "**Fang mit Hangul an!** Das Alphabet hat nur 24 Grundzeichen und ist in "
        "1–2 Wochen drin. Sobald du Silben lesen kannst, macht alles andere "
        "viel mehr Spaß 🎉"
    )

# ── Reset ─────────────────────────────────────────────────────────────────────
if st.button("🔄 Statistik zurücksetzen", use_container_width=True):
    for k in ["total_cards_seen", "cards_flipped", "correct_answers"]:
        st.session_state[k] = 0
    st.rerun()

st.markdown(
    '<div class="footer">학습 화이팅! · Viel Erfolg 🌟 · Made with ❤️ by Sujin</div>',
    unsafe_allow_html=True,
)
