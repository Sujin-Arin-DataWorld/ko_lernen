"""🇰🇷 Koreanisch lernen — Persönlicher Trainer"""
import sys, pathlib
import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).parent))

# Page title personalisiert (Query-Param wird vor set_page_config gelesen)
_qn = (st.query_params.get("name") or "").strip()[:30]
_pt = f"🇰🇷 Koreanisch für {_qn}" if _qn else "🇰🇷 Koreanisch lernen"

st.set_page_config(
    page_title=_pt,
    page_icon="🇰🇷",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from lib.user import require_user, os_emoji, os_label, clear_user

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

/* ── Level pip row (Streamlit buttons styled) ────────────────────────── */
div[data-testid="stHorizontalBlock"]:has(.lvlmark) [data-testid="stButton"] > button {
    width: 100% !important; min-width: 0 !important;
    aspect-ratio: 1 !important; height: auto !important;
    padding: 0 !important;
    border-radius: 50% !important; border: 2px solid transparent !important;
    background: #f1f3f5 !important; color: #adb5bd !important;
    font-size: .8rem !important; font-weight: 700 !important;
}
.lvlmark { display: none; }
.lvl-cap {
    text-align: center; font-size: .68rem; font-weight: 700;
    margin: 4px 0 0; letter-spacing: -.02em;
}

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
    div[data-testid="stHorizontalBlock"]:has(.lvlmark) [data-testid="stButton"] > button {
        background: #2a2f36 !important; color: #6c757d !important;
    }
    .mod-hangul  { background: linear-gradient(135deg,#2a1525,#3a1a2c); color: #fcc2d7; border-color: #d6336c; }
    .mod-vocab   { background: linear-gradient(135deg,#0f2942,#162e4d); color: #a5d8ff; border-color: #339af0; }
    .mod-grammar { background: linear-gradient(135deg,#3a2e0e,#2e2616); color: #ffe066; border-color: #f59f00; }
    .mod-listen  { background: linear-gradient(135deg,#0f2a1a,#15321e); color: #b2f2bb; border-color: #51cf66; }
    .footer { color: #6c757d; border-top-color: #2a2f36; }
}
</style>
""", unsafe_allow_html=True)

# ── User & OS ─────────────────────────────────────────────────────────────────
user = require_user()           # blockt mit Onboarding falls noch kein Name
_name = user["name"]
_os   = user["os"]

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="hero-title">🇰🇷 한국어 — Koreanisch</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="hero-sub">안녕 {_name}! 오늘도 화이팅 💪</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="hero-meta">{os_emoji(_os)} {os_label(_os)} · Level <b>{LEVELS[current]}</b></p>',
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
st.markdown(
    '<div class="section-h">📈 Dein Level <span class="sh-aside">Tippen zum Setzen</span></div>',
    unsafe_allow_html=True,
)

def _render_pip_row(indices):
    st.markdown('<div class="lvlmark"></div>', unsafe_allow_html=True)
    cols = st.columns(len(indices))
    for col, i in zip(cols, indices):
        lvl = LEVELS[i]
        if i < current:
            label, color = "✓", "#51cf66"
        elif i == current:
            label, color = "📍", "#845ef7"
        else:
            label, color = "·", "#adb5bd"
        if col.button(label, key=f"lvl_{i}", help=f"Auf {lvl} setzen"):
            st.session_state.current_level_idx = i
            st.rerun()
        col.markdown(f'<div class="lvl-cap" style="color:{color}">{lvl}</div>', unsafe_allow_html=True)

_render_pip_row(range(4))
_render_pip_row(range(4, 8))
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
rc1, rc2 = st.columns(2)
with rc1:
    if st.button("🔄 Statistik zurücksetzen", use_container_width=True):
        for k in ["total_cards_seen", "cards_flipped", "correct_answers"]:
            st.session_state[k] = 0
        st.rerun()
with rc2:
    if st.button(f"👤 Nicht {_name}?", use_container_width=True, help="Name zurücksetzen"):
        clear_user()
        st.rerun()

st.markdown(
    f'<div class="footer">학습 화이팅! · Viel Erfolg, {_name} 🌟 · Made with ❤️ by Sujin</div>',
    unsafe_allow_html=True,
)
