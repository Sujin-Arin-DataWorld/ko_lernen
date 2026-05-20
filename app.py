"""🇰🇷 Koreanisch lernen — Persönlicher Trainer für Christian"""
import streamlit as st

st.set_page_config(
    page_title="🇰🇷 Koreanisch für Christian",
    page_icon="🇰🇷",
    layout="wide",
    initial_sidebar_state="expanded",
)

_DEFAULTS = {
    "total_cards_seen": 0,
    "cards_flipped":    0,
    "correct_answers":  0,
    "tts_cache":        {},
    "tts_voice_label":  "Sun-Hi — Weiblich (Seoul)",
    "tts_speed_label":  "📖 Lerntempo",
}
for k, v in _DEFAULTS.items():
    st.session_state.setdefault(k, v)

st.markdown("""
<style>
.home-card {
    display: block; text-decoration: none !important;
    border-radius: 14px; padding: 1.6rem 1.8rem;
    cursor: pointer; transition: transform .18s, box-shadow .18s;
}
.home-card * { text-decoration: none !important; }
.home-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,.15); }
.home-card h2 { margin: 0 0 .4rem; font-size: 1.4rem; }
.home-card p  { margin: 0; font-size: .98rem; opacity: .9; line-height: 1.6; }
.card-hangul  { border:2px solid #e64980; background:linear-gradient(135deg,#fff0f6,#fce4ec); color:#880e4f; }
.card-vocab   { border:2px solid #339af0; background:linear-gradient(135deg,#e7f5ff,#d0ebff); color:#1864ab; }
.card-grammar { border:2px solid #f59f00; background:linear-gradient(135deg,#fff9db,#ffec99); color:#7d4a00; }
.card-listen  { border:2px solid #51cf66; background:linear-gradient(135deg,#ebfbee,#d3f9d8); color:#2b8a3e; }
.level-pip { display:inline-block; width:28px; height:28px; border-radius:50%;
             line-height:28px; text-align:center; font-size:.75rem; font-weight:700; margin:2px; }
/* Level-Buttons als runde Pips */
div[data-testid="stHorizontalBlock"]:has(.lvlmark) [data-testid="stButton"] > button {
    width:42px !important; height:42px !important; border-radius:50% !important;
    padding:0 !important; font-size:.8rem !important; font-weight:700 !important;
    margin:0 auto !important; display:block !important;
}
.lvlmark { display:none; }
.lvl-cap { text-align:center; font-size:.78rem; font-weight:700; margin-top:4px; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🇰🇷 한국어 배우기")
st.markdown("## Willkommen, Christian! 안녕하세요! 👋")
st.caption("Dein persönlicher Koreanisch-Trainer · A1.1 → B2 · Viel Erfolg! 화이팅! 💪")

st.markdown("---")

# ── Level-Fortschritt ─────────────────────────────────────────────────────────
st.subheader("📊 Dein Fortschritt")
st.caption("Klicke ein Level an, um es als aktuell zu markieren")

LEVELS = ["A1.1", "A1.2", "A2.1", "A2.2", "B1.1", "B1.2", "B2.1", "B2"]
st.session_state.setdefault("current_level_idx", 0)
current = st.session_state.current_level_idx

st.markdown('<div class="lvlmark"></div>', unsafe_allow_html=True)
cols = st.columns(len(LEVELS))
for i, (col, lvl) in enumerate(zip(cols, LEVELS)):
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

st.progress((current + 0.5) / len(LEVELS))

# ── Heutige Statistik ─────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📈 Heutige Lernstatistik")
m1, m2, m3, m4 = st.columns(4)
seen    = st.session_state.total_cards_seen
correct = st.session_state.correct_answers
m1.metric("Karten gesehen",   seen)
m2.metric("Karten umgedreht", st.session_state.cards_flipped)
m3.metric("Richtig",          correct)
m4.metric("Genauigkeit",      f"{int(correct/max(1,seen)*100)} %")

# ── Lernmodule ────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🎯 Lernmodule — Was möchtest du üben?")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.markdown("""
    <a href="/한글연습" target="_self" class="home-card card-hangul">
        <h2>🔤 한글 연습 — Hangul</h2>
        <p>Das koreanische Alphabet von Grund auf<br>
           Konsonanten · Vokale · Silbenstruktur<br>
           <em>Empfehlung: Hier starten! ✨</em></p>
    </a>""", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <a href="/단어장" target="_self" class="home-card card-vocab">
        <h2>📚 단어장 — Vokabeln</h2>
        <p>A1 → B2 Vokabelkarten mit Aussprache<br>
           🔊 Koreanische TTS-Aussprache<br>
           Nach Level und Thema filtern</p>
    </a>""", unsafe_allow_html=True)

with col3:
    st.markdown("""
    <a href="/문법카드" target="_self" class="home-card card-grammar">
        <h2>📝 문법 — Grammatik</h2>
        <p>Grammatikmuster auf Deutsch erklärt<br>
           Mit Beispielsätzen und Merkhilfen<br>
           A1 bis B2 — Schritt für Schritt</p>
    </a>""", unsafe_allow_html=True)

with col4:
    st.markdown("""
    <a href="/듣기연습" target="_self" class="home-card card-listen">
        <h2>🎧 듣기 — Hören</h2>
        <p>Koreanische Sätze hören & mitlesen<br>
           Aussprache und Intonation trainieren<br>
           Geschwindigkeitskontrolle</p>
    </a>""", unsafe_allow_html=True)

# ── Tipp des Tages ────────────────────────────────────────────────────────────
st.markdown("---")
st.info("💡 **Lerntipp:** Fang mit Hangul an! Das koreanische Alphabet hat nur 24 Grundzeichen und kann in 1–2 Wochen gelernt werden. Dann macht alles andere viel mehr Spaß! 🎉")

if st.button("🔄 Statistik zurücksetzen"):
    for k in ["total_cards_seen", "cards_flipped", "correct_answers"]:
        st.session_state[k] = 0
    st.rerun()

st.caption("학습 화이팅! · Viel Erfolg beim Lernen, Christian! 🌟 · Made with ❤️ by Sujin")
