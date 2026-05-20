"""🔤 Hangul-Übung — Das koreanische Alphabet"""
import random, sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.tts import VOICES, SPEED_PRESETS, audio_html, get_cached_audio

st.set_page_config(page_title="🔤 Hangul", page_icon="🔤", layout="centered", initial_sidebar_state="expanded")

# ── Daten ─────────────────────────────────────────────────────────────────────
CONSONANTS = [
    ("ㄱ", "g/k", "wie 'g' in Gabe (am Wortanfang) oder 'k' (am Wortende)"),
    ("ㄴ", "n",   "wie 'n' in Name"),
    ("ㄷ", "d/t", "wie 'd' in Dach (Anfang) oder 't' (Ende)"),
    ("ㄹ", "r/l", "zwischen 'r' und 'l' — rollendes r vor Vokal"),
    ("ㅁ", "m",   "wie 'm' in Mutter"),
    ("ㅂ", "b/p", "wie 'b' in Ball (Anfang) oder 'p' (Ende)"),
    ("ㅅ", "s",   "wie 's' in Sonne"),
    ("ㅇ", "–/ng","stumm am Silbenanfang · 'ng' am Silbenende"),
    ("ㅈ", "j",   "wie 'j' in Jahr"),
    ("ㅊ", "ch",  "wie 'ch' in Tschüss — aspiriert (mit Atemhauch)"),
    ("ㅋ", "k",   "wie 'k' in Kalt — stark aspiriert"),
    ("ㅌ", "t",   "wie 't' in Tisch — stark aspiriert"),
    ("ㅍ", "p",   "wie 'p' in Park — stark aspiriert"),
    ("ㅎ", "h",   "wie 'h' in Haus"),
    ("ㄲ", "kk",  "doppeltes ㄱ — gespannt/hart, wie 'k' ohne Aspiration"),
    ("ㄸ", "tt",  "doppeltes ㄷ — gespannt, wie 't' ohne Aspiration"),
    ("ㅃ", "pp",  "doppeltes ㅂ — gespannt, wie 'p' ohne Aspiration"),
    ("ㅆ", "ss",  "doppeltes ㅅ — gespannt, stärker als 's'"),
    ("ㅉ", "jj",  "doppeltes ㅈ — gespannt"),
]

VOWELS = [
    ("ㅏ", "a",   "wie 'a' in Vater · Beispiel: 아 [a]"),
    ("ㅑ", "ya",  "wie 'ja' · Beispiel: 야 [ya]"),
    ("ㅓ", "eo",  "wie 'ö' ohne Lippenrundung · Beispiel: 어 [eo]"),
    ("ㅕ", "yeo", "wie 'yö' · Beispiel: 여 [yeo]"),
    ("ㅗ", "o",   "wie 'o' in Mond · Beispiel: 오 [o]"),
    ("ㅛ", "yo",  "wie 'yo' · Beispiel: 요 [yo]"),
    ("ㅜ", "u",   "wie 'u' in Mund · Beispiel: 우 [u]"),
    ("ㅠ", "yu",  "wie 'yu' · Beispiel: 유 [yu]"),
    ("ㅡ", "eu",  "wie 'ü' ohne Lippenrundung — kein dt. Äquivalent · 으 [eu]"),
    ("ㅣ", "i",   "wie 'i' in Igel · Beispiel: 이 [i]"),
    ("ㅐ", "ae",  "wie 'ä' in Käse · Beispiel: 애 [ae]"),
    ("ㅔ", "e",   "wie 'e' in Bett · Beispiel: 에 [e]"),
    ("ㅘ", "wa",  "Kombination ㅗ+ㅏ · Beispiel: 와 [wa]"),
    ("ㅝ", "wo",  "Kombination ㅜ+ㅓ · Beispiel: 워 [wo]"),
    ("ㅢ", "ui",  "Kombination ㅡ+ㅣ · Beispiel: 의 [ui]"),
]

SYLLABLES = [
    ("가", "ga", "ㄱ + ㅏ"), ("나", "na", "ㄴ + ㅏ"), ("다", "da", "ㄷ + ㅏ"),
    ("라", "ra", "ㄹ + ㅏ"), ("마", "ma", "ㅁ + ㅏ"), ("바", "ba", "ㅂ + ㅏ"),
    ("사", "sa", "ㅅ + ㅏ"), ("아", "a",  "ㅇ + ㅏ"), ("자", "ja", "ㅈ + ㅏ"),
    ("하", "ha", "ㅎ + ㅏ"), ("이", "i",  "ㅇ + ㅣ"), ("우", "u",  "ㅇ + ㅜ"),
    ("오", "o",  "ㅇ + ㅗ"), ("에", "e",  "ㅇ + ㅔ"), ("고", "go", "ㄱ + ㅗ"),
    ("도", "do", "ㄷ + ㅗ"), ("모", "mo", "ㅁ + ㅗ"), ("보", "bo", "ㅂ + ㅗ"),
    ("소", "so", "ㅅ + ㅗ"), ("호", "ho", "ㅎ + ㅗ"), ("구", "gu", "ㄱ + ㅜ"),
    ("수", "su", "ㅅ + ㅜ"), ("부", "bu", "ㅂ + ㅜ"), ("무", "mu", "ㅁ + ㅜ"),
    ("한", "han","ㅎ + ㅏ + ㄴ"), ("국", "guk","ㄱ + ㅜ + ㄱ"), ("말", "mal","ㅁ + ㅏ + ㄹ"),
    ("밥", "bap","ㅂ + ㅏ + ㅂ"), ("집", "jip","ㅈ + ㅣ + ㅂ"), ("책", "chaek","ㅊ + ㅐ + ㄱ"),
]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.hangul-char { font-size:5rem; font-weight:700; text-align:center; line-height:1.1;
               margin:.5rem 0; color:#e64980; }
.rom-text    { font-size:1.8rem; text-align:center; color:#845ef7; font-weight:600; }
.desc-text   { font-size:1.1rem; text-align:center; color:#555; margin:.5rem 0; }
.fc-hangul   { background:#fff0f6; border:3px solid #e64980; border-radius:20px;
               padding:2.5rem 2rem; text-align:center; min-height:260px;
               display:flex; flex-direction:column; justify-content:center; }
@media (prefers-color-scheme: dark) {
    .fc-hangul { background:#2a1525; border-color:#f06595; }
    .hangul-char { color:#f06595; }
    .desc-text { color:#adb5bd; }
}
/* Flip-Overlay */
[data-testid="stVerticalBlock"]:has(.fc-hangul) { position:relative !important; }
[data-testid="stVerticalBlock"]:has(.fc-hangul) [data-testid="stForm"] {
    position:absolute !important; inset:0 !important; border:none !important;
    padding:0 !important; margin:0 !important; background:transparent !important; z-index:10 !important;
}
[data-testid="stForm"] [data-testid="stVerticalBlock"],
[data-testid="stForm"] [data-testid="element-container"],
[data-testid="stForm"] [data-testid="stFormSubmitButton"],
[data-testid="stForm"] [data-testid="stButton"] {
    position:static !important; overflow:visible !important; padding:0 !important; margin:0 !important; gap:0 !important;
}
[data-testid="stForm"] button {
    position:absolute !important; top:0 !important; left:0 !important;
    width:100% !important; height:100% !important;
    background:transparent !important; border:none !important;
    opacity:0 !important; cursor:pointer !important; z-index:100 !important;
    border-radius:20px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar TTS ───────────────────────────────────────────────────────────────
for k, v in {"tts_voice_label": "Sun-Hi — Weiblich (Seoul)", "tts_speed_label": "📖 Lerntempo", "tts_cache": {}}.items():
    st.session_state.setdefault(k, v)

with st.sidebar:
    st.header("🔊 Aussprache")
    voice_label = st.selectbox("Stimme", list(VOICES.keys()),
                               index=list(VOICES.keys()).index(st.session_state.tts_voice_label))
    st.session_state.tts_voice_label = voice_label
    voice = VOICES[voice_label]
    speed_label = st.radio("Tempo", list(SPEED_PRESETS.keys()),
                           index=list(SPEED_PRESETS.keys()).index(st.session_state.tts_speed_label),
                           horizontal=True, label_visibility="collapsed")
    st.session_state.tts_speed_label = speed_label
    rate = f"{SPEED_PRESETS[speed_label]:+d}%"
    st.divider()
    st.markdown("""
    ### 💡 Hangul-Tipps
    - Jede Silbe ist ein **Quadrat**
    - Struktur: **자음 + 모음** (Konsonant + Vokal)
    - Optional: **받침** (Endkonsonant unten)
    - Lese-Reihenfolge: links → rechts, oben → unten
    """)

# ── Hauptinhalt ───────────────────────────────────────────────────────────────
st.title("🔤 한글 연습 — Hangul lernen")
st.caption("Das koreanische Alphabet — 14 Konsonanten + 10 Vokale = unbegrenzte Silben")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Übersicht", "자음 Konsonanten", "모음 Vokale", "🃏 Karten-Übung"])

# ── Tab 1: Übersicht ──────────────────────────────────────────────────────────
with tab1:
    st.subheader("Das Hangul-System")
    st.markdown("""
    Hangul (한글) wurde **1443** vom koreanischen König Sejong erfunden.
    Es ist eines der **wissenschaftlichsten Schriftsysteme** der Welt — jedes Zeichen
    spiegelt die Mund- und Zungenstellung beim Sprechen wider.

    **Silbenstruktur:**
    ```
    한 = ㅎ (h) + ㅏ (a) + ㄴ (n) = "han"
    국 = ㄱ (g) + ㅜ (u) + ㄱ (k) = "guk"
    ```
    """)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 자음 (Konsonanten) — 14 Grundzeichen")
        rows = [CONSONANTS[i:i+5] for i in range(0, 14, 5)] + [CONSONANTS[14:]]
        for row in rows:
            cols = st.columns(len(row))
            for col, (char, rom, _) in zip(cols, row):
                col.markdown(f"<div style='text-align:center;font-size:2rem;font-weight:700;color:#e64980'>{char}</div>"
                             f"<div style='text-align:center;font-size:.85rem;color:#845ef7'>[{rom}]</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("#### 모음 (Vokale) — 10 Grundzeichen")
        rows = [VOWELS[:5], VOWELS[5:10]]
        for row in rows:
            cols = st.columns(len(row))
            for col, (char, rom, _) in zip(cols, row):
                col.markdown(f"<div style='text-align:center;font-size:2rem;font-weight:700;color:#339af0'>{char}</div>"
                             f"<div style='text-align:center;font-size:.85rem;color:#1971c2'>[{rom}]</div>", unsafe_allow_html=True)

# ── Tab 2: Konsonanten ────────────────────────────────────────────────────────
with tab2:
    st.subheader("자음 — Konsonanten")
    for char, rom, desc in CONSONANTS:
        with st.expander(f"**{char}** — [{rom}]"):
            c1, c2 = st.columns([1, 3])
            c1.markdown(f"<div style='font-size:5rem;text-align:center;color:#e64980'>{char}</div>", unsafe_allow_html=True)
            c2.markdown(f"**Aussprache:** [{rom}]  \n{desc}")
            if c2.button("🔊 Hören", key=f"con_{char}"):
                try:
                    ab = get_cached_audio(char, voice, rate)
                    c2.markdown(audio_html(ab, compact=True), unsafe_allow_html=True)
                except Exception as e:
                    c2.error(str(e))

# ── Tab 3: Vokale ─────────────────────────────────────────────────────────────
with tab3:
    st.subheader("모음 — Vokale")
    for char, rom, desc in VOWELS:
        with st.expander(f"**{char}** — [{rom}]"):
            c1, c2 = st.columns([1, 3])
            c1.markdown(f"<div style='font-size:5rem;text-align:center;color:#339af0'>{char}</div>", unsafe_allow_html=True)
            c2.markdown(f"**Aussprache:** [{rom}]  \n{desc}")
            if c2.button("🔊 Hören", key=f"vow_{char}"):
                try:
                    ab = get_cached_audio(char, voice, rate)
                    c2.markdown(audio_html(ab, compact=True), unsafe_allow_html=True)
                except Exception as e:
                    c2.error(str(e))

# ── Tab 4: Kartenübung ────────────────────────────────────────────────────────
with tab4:
    st.subheader("🃏 Kartenübung")

    mode = st.radio("Übungsmodus", ["자음 Konsonanten", "모음 Vokale", "음절 Silben"], horizontal=True)

    if mode == "자음 Konsonanten":
        pool = CONSONANTS
    elif mode == "모음 Vokale":
        pool = VOWELS
    else:
        pool = SYLLABLES

    st.session_state.setdefault("hangul_idx", 0)
    st.session_state.setdefault("hangul_show", False)
    st.session_state.setdefault("hangul_pool_key", mode)

    if st.session_state.hangul_pool_key != mode:
        st.session_state.hangul_pool_key = mode
        st.session_state.hangul_idx      = 0
        st.session_state.hangul_show     = False

    idx  = st.session_state.hangul_idx % len(pool)
    item = pool[idx]
    char, rom, desc = item

    st.progress((idx + 1) / len(pool))
    st.caption(f"{idx + 1} / {len(pool)}")

    # Karteninhalt
    if st.session_state.hangul_show:
        card_html = f"""<div class="fc-hangul">
            <div class="hangul-char">{char}</div>
            <div class="rom-text">[{rom}]</div>
            <div class="desc-text">{desc}</div>
        </div>"""
    else:
        card_html = f"""<div class="fc-hangul">
            <div class="hangul-char">{char}</div>
            <div class="desc-text" style="color:#ccc">👆 Karte anklicken für Aussprache</div>
        </div>"""

    with st.container():
        st.markdown(card_html, unsafe_allow_html=True)
        with st.form(key="hangul_flip"):
            if st.form_submit_button("", use_container_width=True):
                st.session_state.hangul_show = not st.session_state.hangul_show
                st.rerun()

    # TTS + Navigation
    tts_col, _, nav_col = st.columns([2, 1, 3])
    if tts_col.button("🔊 Aussprechen", use_container_width=True):
        try:
            ab = get_cached_audio(char, voice, rate)
            tts_col.markdown(audio_html(ab, compact=True), unsafe_allow_html=True)
        except Exception as e:
            st.error(str(e))

    n1, n2, n3 = nav_col.columns(3)
    if n1.button("⬅️", use_container_width=True, disabled=(idx == 0)):
        st.session_state.hangul_idx  = max(0, idx - 1)
        st.session_state.hangul_show = False
        st.rerun()
    if n2.button("🔀", use_container_width=True):
        st.session_state.hangul_idx  = random.randint(0, len(pool) - 1)
        st.session_state.hangul_show = False
        st.rerun()
    if n3.button("➡️", use_container_width=True, disabled=(idx >= len(pool) - 1)):
        st.session_state.hangul_idx  = min(len(pool) - 1, idx + 1)
        st.session_state.hangul_show = False
        st.rerun()
