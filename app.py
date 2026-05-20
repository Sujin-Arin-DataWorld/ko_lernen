"""🇰🇷 Koreanisch lernen — Persönlicher Trainer für Christian"""
import streamlit as st

st.set_page_config(
    page_title="🇰🇷 Koreanisch für Christian",
    page_icon="🇰🇷",
    layout="centered",
    initial_sidebar_state="collapsed",
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
.block-container { padding-top: .8rem !important; padding-bottom: 2rem !important; }

/* ── 섹션 레이블 ── */
.section-label {
    font-size: .78rem; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; opacity: .5; margin: 1.1rem 0 .45rem;
}

/* ── 레벨 뱃지 카드 ── */
.level-summary {
    display: flex; align-items: center; gap: 1rem;
    background: linear-gradient(135deg,#f3f0ff,#e5dbff);
    border: 1.5px solid #845ef7; border-radius: 14px;
    padding: .85rem 1.1rem; margin-bottom: .45rem;
}
.level-badge {
    background: #845ef7; color: #fff;
    border-radius: 10px; padding: .4rem .85rem;
    font-size: 1.35rem; font-weight: 900;
    letter-spacing: .03em; line-height: 1; white-space: nowrap;
    min-width: 3.8rem; text-align: center;
}
.level-meta { color: #5f3dc4; font-size: .86rem; line-height: 1.5; }
.level-meta strong { font-size: .92rem; display: block; margin-bottom: .1rem; }

/* ── 통계 그리드 ── */
.stats-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: .5rem; margin-bottom: .3rem;
}
.stat-card {
    border-radius: 12px; padding: .8rem .9rem; text-align: center;
    background: rgba(130,130,160,.1); border: 1px solid rgba(130,130,160,.18);
}
.stat-num { font-size: 1.65rem; font-weight: 800; line-height: 1; margin-bottom: .2rem; }
.stat-label { font-size: .7rem; font-weight: 600; opacity: .55; text-transform: uppercase; letter-spacing: .05em; }

/* ── 모듈 카드 ── */
.home-card {
    display: flex; align-items: center; gap: 1rem;
    text-decoration: none !important;
    border-radius: 14px; padding: 1rem 1.15rem;
    cursor: pointer; transition: transform .18s, box-shadow .18s;
    margin-bottom: .55rem;
}
.home-card * { text-decoration: none !important; }
.home-card:active { transform: scale(.98); }
.home-card-icon { font-size: 2rem; flex-shrink: 0; line-height: 1; }
.home-card-body h3 { margin: 0 0 .2rem; font-size: 1.05rem; font-weight: 800; }
.home-card-body p  { margin: 0; font-size: .82rem; opacity: .85; line-height: 1.45; }
.card-hangul  { border:2px solid #e64980; background:linear-gradient(135deg,#fff0f6,#fce4ec); color:#880e4f; }
.card-vocab   { border:2px solid #339af0; background:linear-gradient(135deg,#e7f5ff,#d0ebff); color:#1864ab; }
.card-grammar { border:2px solid #f59f00; background:linear-gradient(135deg,#fff9db,#ffec99); color:#7d4a00; }
.card-listen  { border:2px solid #51cf66; background:linear-gradient(135deg,#ebfbee,#d3f9d8); color:#2b8a3e; }

@media (max-width: 640px) {
    .level-badge { font-size: 1.1rem; min-width: 3.2rem; }
    .stat-num    { font-size: 1.45rem; }
    .home-card-body h3 { font-size: .98rem; }
    .home-card-body p  { font-size: .78rem; }
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("### 🇰🇷 Willkommen, Christian! 안녕하세요! 👋")
st.caption("Persönlicher Koreanisch-Trainer · A1.1 → B2 · 화이팅! 💪")

# ── Level-Fortschritt ─────────────────────────────────────────────────────────
LEVELS = ["A1.1", "A1.2", "A2.1", "A2.2", "B1.1", "B1.2", "B2.1", "B2"]
st.session_state.setdefault("current_level_idx", 0)
current = st.session_state.current_level_idx
pct = int((current + 1) / len(LEVELS) * 100)

st.markdown('<p class="section-label">📊 Dein Fortschritt</p>', unsafe_allow_html=True)
st.markdown(f"""
<div class="level-summary">
  <div class="level-badge">{LEVELS[current]}</div>
  <div class="level-meta">
    <strong>Level {current + 1} von {len(LEVELS)}</strong>
    {pct} % abgeschlossen
  </div>
</div>
""", unsafe_allow_html=True)
st.progress((current + 0.5) / len(LEVELS))

with st.expander("✏️ Level ändern"):
    selected = st.select_slider(
        "Level wählen",
        options=LEVELS,
        value=LEVELS[current],
        label_visibility="collapsed",
    )
    new_idx = LEVELS.index(selected)
    if new_idx != current:
        st.session_state.current_level_idx = new_idx
        st.rerun()

# ── Heutige Statistik ─────────────────────────────────────────────────────────
seen     = st.session_state.total_cards_seen
correct  = st.session_state.correct_answers
flipped  = st.session_state.cards_flipped
accuracy = int(correct / max(1, seen) * 100)

st.markdown(f"""
<p class="section-label">📈 Heutige Lernstatistik</p>
<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-num">{seen}</div>
    <div class="stat-label">Gesehen</div>
  </div>
  <div class="stat-card">
    <div class="stat-num">{flipped}</div>
    <div class="stat-label">Umgedreht</div>
  </div>
  <div class="stat-card">
    <div class="stat-num">{correct}</div>
    <div class="stat-label">Richtig</div>
  </div>
  <div class="stat-card">
    <div class="stat-num">{accuracy}%</div>
    <div class="stat-label">Genauigkeit</div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 Statistik zurücksetzen", type="tertiary"):
    for k in ["total_cards_seen", "cards_flipped", "correct_answers"]:
        st.session_state[k] = 0
    st.rerun()

# ── Lernmodule ────────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">🎯 Was möchtest du üben?</p>', unsafe_allow_html=True)

st.markdown("""
<div>
<a href="/한글연습_(Hangul)" target="_self" class="home-card card-hangul">
  <div class="home-card-icon">🔤</div>
  <div class="home-card-body">
    <h3>한글 연습 — Hangul</h3>
    <p>Alphabet · Konsonanten · Vokale · Silben<br><em>✨ Empfehlung: Hier starten!</em></p>
  </div>
</a>
<a href="/단어장_(Vokabeln)" target="_self" class="home-card card-vocab">
  <div class="home-card-icon">📚</div>
  <div class="home-card-body">
    <h3>단어장 — Vokabeln</h3>
    <p>A1 → B2 Karten · TTS-Aussprache · Level-Filter</p>
  </div>
</a>
<a href="/문법카드_(Grammatik)" target="_self" class="home-card card-grammar">
  <div class="home-card-icon">📝</div>
  <div class="home-card-body">
    <h3>문법 — Grammatik</h3>
    <p>Muster auf Deutsch · Beispielsätze · A1–B2</p>
  </div>
</a>
<a href="/듣기연습_(Hören)" target="_self" class="home-card card-listen">
  <div class="home-card-icon">🎧</div>
  <div class="home-card-body">
    <h3>듣기 — Hören</h3>
    <p>Sätze hören &amp; mitlesen · Geschwindigkeitskontrolle</p>
  </div>
</a>
</div>
""", unsafe_allow_html=True)

with st.expander("💡 Lerntipp"):
    st.info("Fang mit **Hangul** an! Das koreanische Alphabet hat nur 24 Grundzeichen — in 1–2 Wochen lernbar. Dann macht alles andere viel mehr Spaß! 🎉")

st.caption("학습 화이팅! · Made with ❤️ by Sujin")
