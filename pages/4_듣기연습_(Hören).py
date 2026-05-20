"""🎧 듣기연습 — Hörübungen mit koreanischen Sätzen"""
import random
import sys, pathlib
import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from lib.tts import VOICES, SPEED_PRESETS, get_cached_audio, audio_html
from lib.data import load_listening_sentences

st.set_page_config(
    page_title="🎧 듣기",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in {
    "listen_idx":       0,
    "listen_show":      False,
    "listen_score":     0,
    "listen_total":     0,
    "tts_voice_label":  "Sun-Hi — Weiblich (Seoul)",
    "tts_speed_label":  "📖 Lerntempo",
}.items():
    st.session_state.setdefault(k, v)

# ── CSS — mobile-first ────────────────────────────────────────────────────────
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
    color: #2b8a3e;
}
.page-sub { font-size: .8rem; color: #868e96; margin: 0 0 .8rem; }

.chips { display: flex; gap: 6px; flex-wrap: wrap; margin: .4rem 0 .8rem; }
.chip {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 4px 10px; border-radius: 100px;
    background: #f1f3f5; color: #495057;
    font-size: .75rem; font-weight: 600;
}
.chip.success { background: #ebfbee; color: #2b8a3e; }
.chip.primary { background: #e7f5ff; color: #1864ab; }

.listen-card {
    border-radius: 18px; padding: 2rem 1.4rem;
    background: linear-gradient(135deg, #ebfbee, #d3f9d8);
    border: 2px solid #51cf66; text-align: center;
    min-height: 180px; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    box-shadow: 0 4px 16px rgba(81, 207, 102, .15);
    margin-bottom: .8rem;
}
.listen-level {
    font-size: .68rem; font-weight: 800; color: #fff;
    background: #51cf66; border-radius: 100px;
    padding: 3px 12px; margin-bottom: .8rem;
    letter-spacing: .04em;
}
.listen-korean  { font-size: 1.7rem; font-weight: 800; color: #2b8a3e; margin: 0 0 .4rem; line-height: 1.25; }
.listen-roman   { font-size: .92rem; color: #4caf50; font-style: italic; margin-bottom: .4rem; }
.listen-german  { font-size: 1.05rem; color: #495057; line-height: 1.4; transition: filter .3s ease; }
.listen-hidden  { filter: blur(8px); user-select: none; cursor: pointer; }
.listen-visible { filter: none; }
.listen-mystery { font-size: 2rem; letter-spacing: .5rem; color: #51cf66; opacity: .6; }

.stButton > button {
    width: 100%; min-height: 44px;
    border-radius: 12px; font-weight: 600;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #51cf66, #37b24d) !important;
    color: #fff !important; border: none !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; height: 0; }

@media (max-width: 480px) {
    .block-container { padding-left: .65rem !important; padding-right: .65rem !important; }
    .listen-card { padding: 1.5rem 1.1rem; min-height: 160px; }
    .listen-korean { font-size: 1.45rem; }
    .listen-german { font-size: .95rem; }
}

@media (prefers-color-scheme: dark) {
    .back-link { color: #adb5bd; }
    .page-title { color: #8ce99a; }
    .page-sub { color: #6c757d; }
    .chip { background: #2a2f36; color: #ced4da; }
    .chip.success { background: #1b3a23; color: #8ce99a; }
    .chip.primary { background: #1d3557; color: #74c0fc; }
    .listen-card {
        background: linear-gradient(135deg, #0f2a1a, #15321e);
        border-color: #51cf66;
    }
    .listen-korean { color: #b2f2bb; }
    .listen-roman { color: #8ce99a; }
    .listen-german { color: #ced4da; }
}
</style>
""", unsafe_allow_html=True)

# ── Daten ─────────────────────────────────────────────────────────────────────
df_s = load_listening_sentences()

# ── Sidebar — TTS + Filter ────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔊 Stimme")
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
        "**📖 So übst du**\n\n"
        "1. ▶ Hören\n"
        "2. Selber überlegen\n"
        "3. Lösung anzeigen\n"
        "4. ✅ / ❌ bewerten\n"
    )
    st.divider()
    if st.button("🔄 Session zurücksetzen", use_container_width=True):
        st.session_state.listen_score = 0
        st.session_state.listen_total = 0
        st.session_state.listen_idx = 0
        st.session_state.listen_show = False
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<a class="back-link" href="/" target="_self">← Zurück</a>', unsafe_allow_html=True)
st.markdown('<h1 class="page-title">🎧 듣기 · Hören</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Höre den Satz · Versuche zu verstehen · Bewerte dich selbst</p>', unsafe_allow_html=True)

# ── Filter (main) ─────────────────────────────────────────────────────────────
with st.expander("🔍 Filter", expanded=False):
    fc1, fc2 = st.columns(2)
    sel_level  = fc1.selectbox("Level",  ["Alle"] + sorted(df_s["level"].unique().tolist()), key="lst_f_level")
    sel_source = fc2.selectbox("Quelle", ["Alle", "Vokabel", "Grammatik"],                   key="lst_f_src")

# ── Filter anwenden ───────────────────────────────────────────────────────────
df_f = df_s.copy()
if sel_level != "Alle":
    df_f = df_f[df_f["level"] == sel_level]
if sel_source != "Alle":
    df_f = df_f[df_f["source"] == sel_source]
df_f = df_f.reset_index(drop=True)

if df_f.empty:
    st.warning("Keine Sätze für diesen Filter.")
    st.stop()

idx = st.session_state.listen_idx % len(df_f)
row = df_f.iloc[idx]

# ── Stat chips ────────────────────────────────────────────────────────────────
acc = int(st.session_state.listen_score / max(1, st.session_state.listen_total) * 100)
st.markdown(f"""
<div class="chips">
    <span class="chip primary">🎧 {idx+1} / {len(df_f)}</span>
    <span class="chip">📋 {st.session_state.listen_total} gehört</span>
    <span class="chip success">✅ {st.session_state.listen_score}</span>
    <span class="chip">🎯 {acc}%</span>
</div>
""", unsafe_allow_html=True)

# ── Modus: Hören vs Diktat vs Liste ──────────────────────────────────────────
tab_listen, tab_dictate, tab_all = st.tabs(["🎧 Hören", "✏️ Diktat", "📋 Liste"])

with tab_listen:
    show = st.session_state.listen_show

    if show:
        card_html = f"""
        <div class="listen-card">
            <div class="listen-level">{row.level} · {row.source}</div>
            <div class="listen-korean">{row.korean}</div>
            <div class="listen-german listen-visible">{row.german}</div>
        </div>"""
    else:
        card_html = f"""
        <div class="listen-card">
            <div class="listen-level">{row.level} · {row.source}</div>
            <div class="listen-mystery">❓ ❓ ❓</div>
            <div class="listen-german listen-hidden">{row.german}</div>
        </div>"""
    st.markdown(card_html, unsafe_allow_html=True)

    if st.button("▶ Satz abspielen", use_container_width=True, type="primary"):
        with st.spinner("Lade Audio…"):
            audio = get_cached_audio(row.korean, voice, speed)
            st.markdown(audio_html(audio), unsafe_allow_html=True)

    if st.button("🐌 Langsamer abspielen", use_container_width=True):
        with st.spinner("Lade Audio…"):
            slow_speed = f"{max(SPEED_PRESETS['🐌 Sehr langsam'], SPEED_PRESETS[speed_label] - 15):+d}%"
            audio = get_cached_audio(row.korean, voice, slow_speed)
            st.markdown(audio_html(audio), unsafe_allow_html=True)

    st.markdown("")

    # Solution / rating buttons
    sol_col1, sol_col2 = st.columns(2)
    with sol_col1:
        if not show:
            if st.button("👁 Lösung anzeigen", use_container_width=True):
                st.session_state.listen_show = True
                st.session_state.listen_total += 1
                st.rerun()
        else:
            if st.button("✅ Verstanden!", use_container_width=True, type="primary"):
                st.session_state.listen_score += 1
                st.session_state.listen_idx = (idx + 1) % len(df_f)
                st.session_state.listen_show = False
                st.rerun()
    with sol_col2:
        if show:
            if st.button("❌ Nochmal", use_container_width=True):
                st.session_state.listen_show = False
                st.rerun()
        else:
            if st.button("⏭ Überspringen", use_container_width=True):
                st.session_state.listen_idx = (idx + 1) % len(df_f)
                st.session_state.listen_show = False
                st.rerun()

    st.markdown("")
    n1, n2, n3 = st.columns(3)
    with n1:
        if st.button("⏮ Erster", use_container_width=True):
            st.session_state.listen_idx = 0
            st.session_state.listen_show = False
            st.rerun()
    with n2:
        if st.button("🔀 Zufällig", use_container_width=True):
            st.session_state.listen_idx = random.randint(0, len(df_f) - 1)
            st.session_state.listen_show = False
            st.rerun()
    with n3:
        if st.button("▶ Nächster", use_container_width=True):
            st.session_state.listen_idx = (idx + 1) % len(df_f)
            st.session_state.listen_show = False
            st.rerun()

    # Hinweis-Schlüsselwort dezent
    st.caption(f"💡 Schlüsselwort: **{row.keyword}**")

with tab_dictate:
    st.subheader("✏️ Diktat")
    st.caption("Höre den Satz und tippe ihn ab (Koreanisch oder Deutsch).")

    if st.button("▶ Satz abspielen", use_container_width=True, type="primary", key="dict_play"):
        with st.spinner("Lade Audio…"):
            audio = get_cached_audio(row.korean, voice, speed)
            st.markdown(audio_html(audio), unsafe_allow_html=True)

    user_input = st.text_input("Deine Antwort:", key="dict_input", placeholder="여기에 입력 · Hier eingeben…")
    if st.button("✔ Überprüfen", key="dict_check", use_container_width=True):
        if not user_input.strip():
            st.warning("Bitte erst antworten!")
        elif row.korean in user_input or row.german.lower() in user_input.lower():
            st.success(f"✅ Richtig! — **{row.korean}** = {row.german}")
        else:
            st.error(f"❌ Nicht ganz. Richtig wäre: **{row.korean}** — {row.german}")

with tab_all:
    show_cols = df_f[["level", "source", "keyword", "korean", "german"]].copy()
    show_cols.columns = ["Level", "Quelle", "Schlüsselwort", "Koreanisch", "Deutsch"]
    st.dataframe(show_cols, use_container_width=True, hide_index=True)
