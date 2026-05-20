"""🎧 듣기연습 — Hörübungen mit koreanischen Sätzen"""
import streamlit as st
import pandas as pd
import sys, pathlib, random
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from lib.tts import VOICES, SPEED_PRESETS, get_cached_audio, audio_html

st.set_page_config(page_title="🎧 듣기 — Hören", page_icon="🎧", layout="wide")

st.markdown("""
<style>
.listen-card {
    border-radius: 14px; padding: 2rem 1.8rem;
    background: linear-gradient(135deg, #ebfbee, #d3f9d8);
    border: 2px solid #51cf66; text-align: center;
    min-height: 180px; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
}
.listen-korean  { font-size: 2rem; font-weight: 700; color: #2b8a3e; margin-bottom: .4rem; }
.listen-roman   { font-size: 1rem; color: #4caf50; font-style: italic; margin-bottom: .4rem; }
.listen-german  { font-size: 1.2rem; color: #495057; }
.listen-hidden  { filter: blur(6px); user-select: none; transition: filter .3s; cursor: pointer; }
.listen-visible { filter: none; }
.level-badge {
    display: inline-block; border-radius: 20px; padding: 2px 12px;
    font-size: .8rem; font-weight: 700; color: #fff;
    background: #51cf66; margin-bottom: .6rem;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in {
    "listen_idx": 0, "listen_show": False,
    "listen_score": 0, "listen_total": 0,
    "tts_voice_label": "Sun-Hi — Weiblich (Seoul)",
    "tts_speed_label": "📖 Lerntempo",
}.items():
    st.session_state.setdefault(k, v)

# ── Daten laden ───────────────────────────────────────────────────────────────
df_vocab   = pd.read_csv(pathlib.Path(__file__).parent.parent / "data" / "korean_vocab.csv")
df_grammar = pd.read_csv(pathlib.Path(__file__).parent.parent / "data" / "grammar.csv")

# Beispielsätze aus beiden CSVs zusammenstellen
sentences = []
for _, r in df_vocab.iterrows():
    if pd.notna(r.example_korean) and len(str(r.example_korean)) > 3:
        sentences.append({
            "korean":  r.example_korean,
            "german":  r.example_german,
            "roman":   "",
            "level":   r.level,
            "topic":   r.topic,
            "source":  "Vokabel",
            "keyword": r.korean,
        })
for _, r in df_grammar.iterrows():
    if pd.notna(r.example_korean) and len(str(r.example_korean)) > 3:
        sentences.append({
            "korean":  r.example_korean,
            "german":  r.example_german,
            "roman":   "",
            "level":   r.level,
            "topic":   r.type_de,
            "source":  "Grammatik",
            "keyword": r.pattern,
        })

df_s = pd.DataFrame(sentences).drop_duplicates(subset=["korean"]).reset_index(drop=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Einstellungen")

    st.subheader("🔊 Stimme")
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
    levels = ["Alle"] + sorted(df_s["level"].unique().tolist())
    sel_level = st.selectbox("Level", levels)
    sources = ["Alle", "Vokabel", "Grammatik"]
    sel_source = st.selectbox("Quelle", sources)

    st.markdown("---")
    st.subheader("📊 Session")
    st.metric("Gehört", st.session_state.listen_total)
    st.metric("Verstanden ✅", st.session_state.listen_score)
    acc = int(st.session_state.listen_score / max(1, st.session_state.listen_total) * 100)
    st.metric("Genauigkeit", f"{acc} %")
    if st.button("🔄 Zurücksetzen"):
        st.session_state.listen_score = 0
        st.session_state.listen_total = 0
        st.rerun()

    st.markdown("---")
    st.markdown("""
    **📖 So übst du:**
    1. Klicke ▶ und höre genau zu
    2. Versuche den Satz zu verstehen
    3. Klicke **Lösung anzeigen**
    4. Bewerte dich selbst ✅ / ❌
    """)

# ── Daten filtern ─────────────────────────────────────────────────────────────
df_f = df_s.copy()
if sel_level != "Alle":
    df_f = df_f[df_f["level"] == sel_level]
if sel_source != "Alle":
    df_f = df_f[df_f["source"] == sel_source]
df_f = df_f.reset_index(drop=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎧 듣기연습 — Hörübungen")
st.caption("Höre den koreanischen Satz und versuche ihn zu verstehen, bevor du die Lösung anschaust")

if df_f.empty:
    st.warning("Keine Sätze für diesen Filter.")
    st.stop()

idx = st.session_state.listen_idx % len(df_f)
row = df_f.iloc[idx]

# Fortschritt
st.caption(f"Satz {idx + 1} von {len(df_f)} · Level: {row.level} · {row.source}: {row.keyword}")

# ── Modus: Diktieren oder Hören ───────────────────────────────────────────────
tab_listen, tab_dictate, tab_all = st.tabs(["🎧 Hören & Verstehen", "✏️ Diktieren", "📋 Alle Sätze"])

with tab_listen:
    show = st.session_state.listen_show

    # Karte
    korean_class   = "listen-korean"
    roman_class    = "listen-roman"
    german_class   = f"listen-german {'listen-visible' if show else 'listen-hidden'}"

    card_html = f"""
    <div class="listen-card">
        <div class="level-badge">{row.level} · {row.source}</div>
        <div class="{korean_class}">{row.korean if show else "❓ ❓ ❓"}</div>
        <div class="{german_class}">{row.german}</div>
    </div>"""
    st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Audio automatisch laden
    tts_col1, tts_col2, tts_col3 = st.columns([1, 2, 1])
    with tts_col2:
        if st.button("▶ Satz abspielen", use_container_width=True, type="primary"):
            with st.spinner("Lade Audio…"):
                audio = get_cached_audio(row.korean, voice, speed)
                st.markdown(audio_html(audio, compact=False), unsafe_allow_html=True)

        if st.button("▶ Nochmal langsamer", use_container_width=True):
            with st.spinner("Lade Audio…"):
                slow_speed = f"{max(SPEED_PRESETS['🐌 Sehr langsam'], SPEED_PRESETS[speed_label] - 15):+d}%"
                audio = get_cached_audio(row.korean + "_slow", voice, slow_speed)
                st.markdown(audio_html(audio, compact=False), unsafe_allow_html=True)

    st.markdown("---")

    # Lösung + Bewertung
    sol_col1, sol_col2 = st.columns(2)
    with sol_col1:
        if not show:
            if st.button("👁 Lösung anzeigen", use_container_width=True):
                st.session_state.listen_show = True
                st.session_state.listen_total += 1
                st.rerun()
        else:
            if st.button("✅ Verstanden!", use_container_width=True):
                st.session_state.listen_score += 1
                st.session_state.listen_idx = (idx + 1) % len(df_f)
                st.session_state.listen_show = False
                st.rerun()

    with sol_col2:
        if show:
            if st.button("❌ Nochmal üben", use_container_width=True):
                st.session_state.listen_show = False
                st.rerun()
        else:
            if st.button("⏭ Überspringen", use_container_width=True):
                st.session_state.listen_idx = (idx + 1) % len(df_f)
                st.session_state.listen_show = False
                st.rerun()

    st.markdown("---")
    n1, n2, n3 = st.columns(3)
    with n1:
        if st.button("⏮ Erster Satz", use_container_width=True):
            st.session_state.listen_idx = 0
            st.session_state.listen_show = False
            st.rerun()
    with n2:
        if st.button("🔀 Zufällig", use_container_width=True):
            st.session_state.listen_idx = random.randint(0, len(df_f) - 1)
            st.session_state.listen_show = False
            st.rerun()
    with n3:
        if st.button("▶ Nächster Satz", use_container_width=True):
            st.session_state.listen_idx = (idx + 1) % len(df_f)
            st.session_state.listen_show = False
            st.rerun()

with tab_dictate:
    st.subheader("✏️ Diktierübung")
    st.markdown("Höre den Satz und schreibe ihn auf Koreanisch oder auf Deutsch.")

    d_col1, d_col2 = st.columns([1, 2])
    with d_col1:
        if st.button("▶ Satz abspielen", use_container_width=True, type="primary", key="dict_play"):
            with st.spinner("Lade Audio…"):
                audio = get_cached_audio(row.korean, voice, speed)
                st.markdown(audio_html(audio), unsafe_allow_html=True)

    with d_col2:
        user_input = st.text_input("Deine Antwort (Koreanisch oder Deutsch):", key="dict_input")
        if st.button("✔ Überprüfen", key="dict_check"):
            if user_input.strip():
                if row.korean in user_input or row.german.lower() in user_input.lower():
                    st.success(f"✅ Richtig! — {row.korean} = {row.german}")
                else:
                    st.error(f"❌ Nicht ganz. Richtig wäre: **{row.korean}** — {row.german}")
            else:
                st.warning("Bitte erst antworten!")

with tab_all:
    show_cols = df_f[["level", "source", "keyword", "korean", "german"]].copy()
    show_cols.columns = ["Level", "Quelle", "Schlüsselwort", "Koreanisch", "Deutsch"]
    st.dataframe(show_cols, use_container_width=True, hide_index=True)
