"""🔤 Hangul-Übung — Das koreanische Alphabet"""
import random, sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.tts import VOICES, SPEED_PRESETS, audio_html, get_cached_audio

st.set_page_config(page_title="🔤 Hangul", page_icon="🔤", layout="centered", initial_sidebar_state="collapsed")

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
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Pretendard', 'Noto Sans KR', sans-serif;
    -webkit-tap-highlight-color: transparent;
    -webkit-font-smoothing: antialiased;
}
.block-container {
    padding: .8rem .9rem 2rem .9rem !important;
    max-width: 760px !important;
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
    color: #c2255c;
}
.page-sub { font-size: .8rem; color: #868e96; margin: 0 0 .8rem; }
.stButton > button {
    width: 100%; min-height: 44px;
    border-radius: 12px; font-weight: 600;
}
.hangul-char { font-size:5rem; font-weight:700; text-align:center; line-height:1.1;
               margin:.5rem 0; color:#e64980; }
.rom-text    { font-size:1.8rem; text-align:center; color:#845ef7; font-weight:600; }
.desc-text   { font-size:1.05rem; text-align:center; color:#555; margin:.5rem 0; }
.fc-hangul   { background:linear-gradient(135deg,#fff5f9,#fce4ec); border:2px solid #e64980; border-radius:18px;
               padding:2rem 1.5rem; text-align:center; min-height:240px;
               display:flex; flex-direction:column; justify-content:center;
               box-shadow:0 4px 16px rgba(230,73,128,.15); }
@media (max-width: 480px) {
    .block-container { padding-left: .65rem !important; padding-right: .65rem !important; }
    .page-title { font-size: 1.15rem; }
    .hangul-char { font-size: 4rem; }
    .rom-text { font-size: 1.4rem; }
    .desc-text { font-size: .95rem; }
    .fc-hangul { padding: 1.5rem 1rem; min-height: 200px; }
}
@media (prefers-color-scheme: dark) {
    .back-link { color: #adb5bd; }
    .page-title { color: #faa2c1; }
    .page-sub { color: #6c757d; }
    .fc-hangul { background:linear-gradient(135deg,#2a1525,#3a1a2c); border-color:#f06595; }
    .hangul-char { color:#f06595; }
    .rom-text { color:#d0bfff; }
    .desc-text { color:#adb5bd; }
}

/* ── Streamlit chrome ─────────────────────────────────── */
#MainMenu, footer { visibility: hidden; height: 0; }

/* ── Übersicht: info + grid + detail ──────────────────── */
.info-box {
    background: linear-gradient(135deg, #fff5f9, #f3f0ff);
    border: 1px solid #fcc2d7; border-radius: 12px;
    padding: .65rem .85rem; margin: .3rem 0 .9rem;
    font-size: .82rem; line-height: 1.5; color: #5f3dc4;
}
.section-h-h {
    font-size: .82rem; font-weight: 700; margin: 1rem 0 .5rem;
    color: #495057; display: flex; align-items: center;
    justify-content: space-between; letter-spacing: -.005em;
}
.section-h-h .sh-aside {
    font-size: .68rem; color: #adb5bd; font-weight: 600;
    background: #f1f3f5; padding: 2px 8px; border-radius: 100px;
}

/* Grid buttons — kompakte 5er-Reihen */
div[data-testid="stHorizontalBlock"]:has(.ov-mark) [data-testid="stButton"] > button {
    aspect-ratio: 1 !important;
    padding: 0 !important; min-height: 0 !important;
    font-size: 1.4rem !important; font-weight: 700 !important;
    border-radius: 12px !important;
    border: 1.5px solid #dee2e6 !important;
    background: #fff !important; color: #495057 !important;
    transition: transform .12s ease, border-color .12s, background .12s;
}
div[data-testid="stHorizontalBlock"]:has(.ov-mark) [data-testid="stButton"] > button:hover {
    border-color: #845ef7 !important; background: #f3f0ff !important;
}
div[data-testid="stHorizontalBlock"]:has(.ov-mark) [data-testid="stButton"] > button:active {
    transform: scale(.92);
}
.ov-mark { display: none; }
.ov-rom {
    text-align: center; font-size: .65rem; color: #868e96;
    margin: 3px 0 0; font-weight: 600; font-style: italic;
    letter-spacing: -.02em;
}

.ov-detail {
    margin: .9rem 0 .5rem;
    border-radius: 16px; padding: 1.1rem 1rem;
    background: linear-gradient(135deg, #fff5f9, #fce4ec);
    border: 2px solid #e64980; text-align: center;
    box-shadow: 0 4px 16px rgba(230, 73, 128, .12);
}
.ov-detail-char {
    font-size: 4.5rem; font-weight: 800; color: #c2255c;
    line-height: 1; margin-bottom: .15rem;
}
.ov-detail-rom {
    font-size: 1.1rem; color: #845ef7; font-weight: 700;
    margin-bottom: .35rem; font-style: italic;
}
.ov-detail-desc { font-size: .88rem; color: #495057; line-height: 1.5; }

.syl-demo { display: grid; gap: .35rem; margin-top: .3rem; }
.syl-ex {
    background: #f8f9fa; border: 1px solid #e9ecef;
    border-radius: 10px; padding: .5rem .75rem;
    font-size: .88rem; display: flex; align-items: center;
    gap: .3rem; flex-wrap: wrap;
}
.syl-big   { font-size: 1.6rem; font-weight: 800; color: #1864ab; margin-right: .25rem; }
.syl-plus  { color: #adb5bd; font-weight: 600; }
.syl-arr   { color: #845ef7; font-weight: 700; margin: 0 .15rem; }
.syl-rom   { font-style: italic; color: #845ef7; font-weight: 600; }

@media (max-width: 480px) {
    div[data-testid="stHorizontalBlock"]:has(.ov-mark) [data-testid="stButton"] > button {
        font-size: 1.2rem !important;
    }
    .ov-detail-char { font-size: 3.8rem; }
    .ov-detail-rom  { font-size: 1rem; }
    .ov-detail-desc { font-size: .82rem; }
    .syl-big { font-size: 1.4rem; }
    .syl-ex  { font-size: .82rem; }
}

@media (prefers-color-scheme: dark) {
    .info-box { background: linear-gradient(135deg,#2a1525,#231a35); border-color:#5f3dc4; color:#d0bfff; }
    .section-h-h { color: #ced4da; }
    .section-h-h .sh-aside { background: #2a2f36; color: #6c757d; }
    div[data-testid="stHorizontalBlock"]:has(.ov-mark) [data-testid="stButton"] > button {
        background: #1a1f26 !important; color: #ced4da !important;
        border-color: #343a40 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.ov-mark) [data-testid="stButton"] > button:hover {
        background: #2a1f3e !important; border-color: #845ef7 !important;
    }
    .ov-rom { color: #6c757d; }
    .ov-detail { background: linear-gradient(135deg,#2a1525,#3a1a2c); border-color:#e64980; }
    .ov-detail-char { color: #fcc2d7; }
    .ov-detail-rom  { color: #d0bfff; }
    .ov-detail-desc { color: #ced4da; }
    .syl-ex { background: #1a1f26; border-color: #2a2f36; color: #ced4da; }
    .syl-big { color: #74c0fc; }
    .syl-arr, .syl-rom { color: #d0bfff; }
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
st.markdown('<a class="back-link" href="/" target="_self">← Zurück</a>', unsafe_allow_html=True)
st.markdown('<h1 class="page-title">🔤 한글 연습 · Hangul</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">14 Konsonanten + 10 Vokale = unbegrenzte Silben</p>', unsafe_allow_html=True)

tab1, tab4, tab5 = st.tabs(["📊 Übersicht", "🃏 Karten", "✍️ Schreiben"])

# ── Tab 1: Übersicht — kompaktes Grid + Detail ───────────────────────────────
with tab1:
    st.session_state.setdefault("hangul_selected", "ㄱ")

    st.markdown(
        '<div class="info-box">'
        '<b>한글</b> · 1443 vom König <b>Sejong</b> · jedes Zeichen spiegelt '
        'Mund-/Zungenstellung wider. Silbe = Quadrat.'
        '</div>',
        unsafe_allow_html=True,
    )

    def _ov_grid(chunks, prefix):
        for chunk in chunks:
            st.markdown('<div class="ov-mark"></div>', unsafe_allow_html=True)
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    if i < len(chunk):
                        c, r, _ = chunk[i]
                        if st.button(c, key=f"{prefix}_{c}", use_container_width=True):
                            st.session_state.hangul_selected = c
                            st.rerun()
                        st.markdown(f'<div class="ov-rom">[{r}]</div>', unsafe_allow_html=True)
                    else:
                        st.markdown("&nbsp;", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-h-h">🔥 자음 · Konsonanten <span class="sh-aside">19</span></div>',
        unsafe_allow_html=True,
    )
    _ov_grid([CONSONANTS[i:i+5] for i in range(0, len(CONSONANTS), 5)], "ovc")

    st.markdown(
        '<div class="section-h-h">🌊 모음 · Vokale <span class="sh-aside">15</span></div>',
        unsafe_allow_html=True,
    )
    _ov_grid([VOWELS[i:i+5] for i in range(0, len(VOWELS), 5)], "ovv")

    # ── Detail box for the selected character ────────────────────────────────
    sel  = st.session_state.hangul_selected
    info = next((t for t in CONSONANTS + VOWELS if t[0] == sel), None)
    if info:
        c, r, d = info
        st.markdown(f"""
        <div class="ov-detail">
            <div class="ov-detail-char">{c}</div>
            <div class="ov-detail-rom">[{r}]</div>
            <div class="ov-detail-desc">{d}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔊 Aussprechen", use_container_width=True, key="ov_tts"):
            try:
                ab = get_cached_audio(c, voice, rate)
                st.markdown(audio_html(ab, compact=True), unsafe_allow_html=True)
            except Exception as e:
                st.error(str(e))

    # ── Silbenstruktur — kompakt ─────────────────────────────────────────────
    st.markdown(
        '<div class="section-h-h">🧩 음절 구조 · Silbenaufbau</div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div class="syl-demo">
        <div class="syl-ex"><span class="syl-big">한</span>= ㅎ <span class="syl-plus">+</span> ㅏ <span class="syl-plus">+</span> ㄴ <span class="syl-arr">→</span> <span class="syl-rom">han</span></div>
        <div class="syl-ex"><span class="syl-big">국</span>= ㄱ <span class="syl-plus">+</span> ㅜ <span class="syl-plus">+</span> ㄱ <span class="syl-arr">→</span> <span class="syl-rom">guk</span></div>
        <div class="syl-ex"><span class="syl-big">말</span>= ㅁ <span class="syl-plus">+</span> ㅏ <span class="syl-plus">+</span> ㄹ <span class="syl-arr">→</span> <span class="syl-rom">mal</span></div>
    </div>
    """, unsafe_allow_html=True)

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

# ── Tab 5: Schreiben / Stroke Order ──────────────────────────────────────────
with tab5:
    st.subheader("✍️ 획순 연습 — Strichreihenfolge")
    st.caption("Wähle ein Zeichen · sieh die Strichreihenfolge · übe mit dem Finger")

    STROKE_HTML = """<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,sans-serif;background:transparent;padding:10px;color:#333}
.rules{background:#fff9db;border:1px solid #f59f00;border-radius:10px;padding:10px 14px;margin-bottom:14px}
.rules h3{font-size:.95rem;color:#7d4a00;margin-bottom:8px;font-weight:700}
.rules-list{display:flex;gap:8px;flex-wrap:wrap}
.rule{background:#fff;border-radius:8px;padding:5px 10px;font-size:.82rem;border:1px solid #ffe066;color:#7d4a00}
.rn{color:#e67700;font-weight:700;margin-right:3px}
.mode-tabs{display:flex;gap:8px;margin-bottom:10px}
.mbtn{padding:5px 16px;border-radius:20px;border:2px solid #e64980;background:#fff;color:#e64980;font-weight:600;cursor:pointer;font-size:.88rem}
.mbtn.active{background:#e64980;color:#fff}
.char-grid{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:14px;max-height:280px;overflow-y:auto;padding:4px}
.cbtn{width:44px;height:44px;border-radius:10px;border:2px solid #dee2e6;background:#fff;font-size:1.45rem;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.cbtn.sel{border-color:#339af0;background:#e7f5ff;color:#1864ab}
.cbtn:hover{border-color:#74c0fc;background:#f0f9ff}
.practice-area{display:flex;gap:16px;flex-wrap:wrap}
.cs{flex:1;min-width:210px}
.clabel{font-size:.88rem;font-weight:600;margin-bottom:6px;color:#555}
.char-disp{text-align:center;font-size:1.15rem;font-weight:700;color:#1864ab;margin-bottom:4px;min-height:1.4em}
canvas{border:2px solid #dee2e6;border-radius:12px;display:block;max-width:100%;touch-action:none}
#dc{border-color:#74c0fc;background:#f8fbff}
#pc{border-color:#a9e34b;background:#f8fff4;cursor:crosshair}
.sctrl{display:flex;align-items:center;gap:5px;margin-top:7px;flex-wrap:wrap}
.sbtn{padding:4px 10px;border-radius:8px;border:1px solid #dee2e6;background:#fff;cursor:pointer;font-size:.82rem}
.sbtn:hover{background:#f1f3f5}
.sbtn.pr{background:#339af0;color:#fff;border-color:#339af0}
#si{font-size:.82rem;color:#666;flex:1;text-align:center}
.clrbtn{margin-top:7px;padding:4px 14px;border-radius:8px;border:1px solid #ff6b6b;background:#fff;color:#ff6b6b;cursor:pointer;font-size:.82rem;width:100%}
.clrbtn:hover{background:#fff5f5}
@media (max-width:480px){
  body{padding:6px}
  .rules{padding:8px 10px}
  .rule{font-size:.72rem;padding:4px 8px}
  .rules h3{font-size:.86rem;margin-bottom:6px}
  .mbtn{font-size:.8rem;padding:4px 12px}
  .cbtn{width:40px;height:40px;font-size:1.3rem}
  .practice-area{gap:10px}
  .clabel{font-size:.82rem}
  .char-disp{font-size:1.05rem}
  .sbtn{font-size:.78rem;padding:4px 8px}
  .cnavbtn{font-size:.82rem;padding:5px 10px}
}
@media (prefers-color-scheme:dark){
  body{color:#ced4da}
  .rules{background:#3a3017;border-color:#f59f00}
  .rules h3{color:#ffd43b}
  .rule{background:#1a1f26;color:#ffd43b;border-color:#5a4519}
  .mbtn{background:#1a1f26;color:#fcc2d7;border-color:#e64980}
  .mbtn.active{background:#e64980;color:#fff}
  .cbtn{background:#1a1f26;color:#ced4da;border-color:#343a40}
  .cbtn.sel{background:#0f2942;color:#74c0fc;border-color:#339af0}
  .cbtn:hover{background:#2a1f3e;border-color:#845ef7}
  #dc{background:#0f1419;border-color:#339af0}
  #pc{background:#0f1f15;border-color:#51cf66}
  .sbtn{background:#1a1f26;color:#ced4da;border-color:#343a40}
  .sbtn:hover{background:#2a2f36}
  .sbtn.pr{background:#339af0;color:#fff;border-color:#339af0}
  .clrbtn{background:#1a1f26;color:#ff8787;border-color:#ff6b6b}
  .clrbtn:hover{background:#3a1a1a}
  .char-disp{color:#74c0fc}
  .clabel{color:#adb5bd}
  #si{color:#adb5bd}
  .cnavbtn{background:#1a1f26;color:#ced4da;border-color:#343a40}
  .cur-char-label{color:#74c0fc}
}
</style></head><body>
<div class="rules">
  <h3>✏️ 한글 쓰기 3원칙</h3>
  <div class="rules-list">
    <div class="rule"><span class="rn">①</span>위에서 아래로 (Oben → Unten)</div>
    <div class="rule"><span class="rn">②</span>가로 먼저, 세로 나중 (Horizontal → Vertikal)</div>
    <div class="rule"><span class="rn">③</span>왼쪽에서 오른쪽으로 (Links → Rechts)</div>
  </div>
</div>
<div class="mode-tabs">
  <button class="mbtn active" id="btn-con" onclick="setMode('c',this)">자음 Konsonanten</button>
  <button class="mbtn" id="btn-vow" onclick="setMode('v',this)">모음 Vokale</button>
</div>
<div class="char-grid" id="cg"></div>
<div class="practice-area">
  <div class="cs">
    <div class="clabel">📽 획순 (Strichreihenfolge)</div>
    <div class="char-disp" id="cd">ㄱ</div>
    <canvas id="dc" width="220" height="220"></canvas>
    <div class="sctrl">
      <button class="sbtn" onclick="prevS()">◀</button>
      <span id="si">Strich 1/2</span>
      <button class="sbtn" onclick="nextS()">▶</button>
      <button class="sbtn pr" onclick="animAll()">▶▶ Alle</button>
      <button class="sbtn" onclick="resetD()">↺</button>
    </div>
  </div>
  <div class="cs">
    <div class="clabel">✍️ 연습 (Üben) — mit dem Finger!</div>
    <div class="char-disp" style="color:#2b8a3e">Schreibe nach!</div>
    <div class="canvas-wrap"><canvas id="pc" width="220" height="220"></canvas><div id="praise">Toll! 👏</div></div>
    <button class="clrbtn" onclick="clearP()">🗑 Löschen</button>
    <div class="cnav">
      <button class="cnavbtn" onclick="navChar(-1)">◀ 이전</button>
      <span class="cur-char-label" id="cl">1 / 19</span>
      <button class="cnavbtn" onclick="navChar(1)">다음 ▶</button>
    </div>
  </div>
</div>
<style>
.cnav{display:flex;align-items:center;justify-content:space-between;margin-top:8px;gap:6px}
.cnavbtn{padding:5px 14px;border-radius:10px;border:2px solid #dee2e6;background:#fff;cursor:pointer;font-size:.88rem;font-weight:600}
.cnavbtn:hover{background:#f1f3f5;border-color:#adb5bd}
.cur-char-label{font-size:1rem;font-weight:700;color:#1864ab;text-align:center;flex:1}
.canvas-wrap{position:relative;display:inline-block;line-height:0}
#praise{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%) scale(.85);
  background:rgba(43,138,62,0.95);color:#fff;border-radius:18px;
  padding:14px 26px;font-size:1.5rem;font-weight:700;
  pointer-events:none;opacity:0;transition:opacity .35s, transform .35s;
  z-index:999;text-align:center;white-space:nowrap;line-height:1.2;
  box-shadow:0 6px 20px rgba(43,138,62,0.4)}
#praise.show{opacity:1;transform:translate(-50%,-50%) scale(1)}
</style>
<script>
const S={
 'ㄱ':[{t:'l',p:[[30,55],[172,55],[172,178]]}],
 'ㄴ':[{t:'l',p:[[42,28],[42,170],[178,170]]}],
 'ㄷ':[{t:'l',p:[[35,42],[175,42]]},{t:'l',p:[[35,42],[35,168],[175,168]]}],
 'ㄹ':[{t:'l',p:[[35,42],[170,42],[170,110]]},{t:'l',p:[[35,110],[170,110]]},{t:'l',p:[[35,112],[35,175],[170,175]]}],
 'ㅁ':[{t:'l',p:[[42,42],[42,175]]},{t:'l',p:[[42,42],[172,42],[172,175]]},{t:'l',p:[[42,175],[172,175]]}],
 'ㅂ':[{t:'l',p:[[62,38],[62,178]]},{t:'l',p:[[152,38],[152,178]]},{t:'l',p:[[62,108],[152,108]]},{t:'l',p:[[62,178],[152,178]]}],
 'ㅅ':[{t:'l',p:[[110,40],[42,172]]},{t:'l',p:[[110,40],[178,172]]}],
 'ㅇ':[{t:'c',cx:110,cy:110,r:68}],
 'ㅈ':[{t:'l',p:[[28,60],[192,60]]},{t:'l',p:[[110,60],[45,172]]},{t:'l',p:[[110,60],[175,172]]}],
 'ㅊ':[{t:'l',p:[[85,26],[135,26]]},{t:'l',p:[[28,60],[192,60]]},{t:'l',p:[[110,60],[45,172]]},{t:'l',p:[[110,60],[175,172]]}],
 'ㅋ':[{t:'l',p:[[30,55],[172,55],[172,178]]},{t:'l',p:[[30,116],[158,116]]}],
 'ㅌ':[{t:'l',p:[[30,42],[175,42]]},{t:'l',p:[[30,42],[30,172],[175,172]]},{t:'l',p:[[30,107],[175,107]]}],
 'ㅍ':[{t:'l',p:[[25,65],[192,65]]},{t:'l',p:[[68,65],[68,162]]},{t:'l',p:[[148,65],[148,162]]},{t:'l',p:[[25,162],[192,162]]}],
 'ㅎ':[{t:'l',p:[[88,22],[130,22]]},{t:'l',p:[[40,55],[178,55]]},{t:'c',cx:110,cy:136,r:52}],
 'ㄲ':[{t:'l',p:[[18,60],[88,60],[88,172]]},{t:'l',p:[[108,60],[178,60],[178,172]]}],
 'ㄸ':[{t:'l',p:[[12,42],[88,42]]},{t:'l',p:[[12,42],[12,165],[88,165]]},{t:'l',p:[[102,42],[178,42]]},{t:'l',p:[[102,42],[102,165],[178,165]]}],
 'ㅃ':[{t:'l',p:[[15,38],[15,178]]},{t:'l',p:[[100,38],[100,178]]},{t:'l',p:[[15,108],[100,108]]},{t:'l',p:[[15,178],[100,178]]},{t:'l',p:[[120,38],[120,178]]},{t:'l',p:[[205,38],[205,178]]},{t:'l',p:[[120,108],[205,108]]},{t:'l',p:[[120,178],[205,178]]}],
 'ㅆ':[{t:'l',p:[[70,40],[30,165]]},{t:'l',p:[[70,40],[110,165]]},{t:'l',p:[[148,40],[108,165]]},{t:'l',p:[[148,40],[188,165]]}],
 'ㅉ':[{t:'l',p:[[15,60],[95,60]]},{t:'l',p:[[55,60],[22,165]]},{t:'l',p:[[55,60],[88,165]]},{t:'l',p:[[105,60],[192,60]]},{t:'l',p:[[148,60],[115,165]]},{t:'l',p:[[148,60],[182,165]]}],
 'ㅏ':[{t:'l',p:[[88,25],[88,195]]},{t:'l',p:[[88,110],[158,110]]}],
 'ㅑ':[{t:'l',p:[[88,25],[88,195]]},{t:'l',p:[[88,78],[158,78]]},{t:'l',p:[[88,138],[158,138]]}],
 'ㅓ':[{t:'l',p:[[48,110],[118,110]]},{t:'l',p:[[118,25],[118,195]]}],
 'ㅕ':[{t:'l',p:[[48,78],[118,78]]},{t:'l',p:[[48,138],[118,138]]},{t:'l',p:[[118,25],[118,195]]}],
 'ㅗ':[{t:'l',p:[[110,42],[110,118]]},{t:'l',p:[[25,118],[195,118]]}],
 'ㅛ':[{t:'l',p:[[75,42],[75,118]]},{t:'l',p:[[145,42],[145,118]]},{t:'l',p:[[25,118],[195,118]]}],
 'ㅜ':[{t:'l',p:[[25,95],[195,95]]},{t:'l',p:[[110,95],[110,178]]}],
 'ㅠ':[{t:'l',p:[[25,95],[195,95]]},{t:'l',p:[[75,95],[75,178]]},{t:'l',p:[[145,95],[145,178]]}],
 'ㅡ':[{t:'l',p:[[22,110],[195,110]]}],
 'ㅣ':[{t:'l',p:[[110,22],[110,195]]}],
 'ㅐ':[{t:'l',p:[[72,25],[72,195]]},{t:'l',p:[[72,110],[145,110]]},{t:'l',p:[[145,25],[145,195]]}],
 'ㅔ':[{t:'l',p:[[42,110],[115,110]]},{t:'l',p:[[115,25],[115,195]]},{t:'l',p:[[155,25],[155,195]]}],
 'ㅘ':[{t:'l',p:[[60,42],[60,108]]},{t:'l',p:[[22,108],[125,108]]},{t:'l',p:[[125,25],[125,195]]},{t:'l',p:[[125,110],[188,110]]}],
 'ㅝ':[{t:'l',p:[[22,92],[120,92]]},{t:'l',p:[[70,92],[70,165]]},{t:'l',p:[[48,118],[120,118]]},{t:'l',p:[[120,25],[120,195]]}],
 'ㅢ':[{t:'l',p:[[30,110],[160,110]]},{t:'l',p:[[160,25],[160,195]]}],
};
const CON=['ㄱ','ㄴ','ㄷ','ㄹ','ㅁ','ㅂ','ㅅ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ','ㄲ','ㄸ','ㅃ','ㅆ','ㅉ'];
const VOW=['ㅏ','ㅑ','ㅓ','ㅕ','ㅗ','ㅛ','ㅜ','ㅠ','ㅡ','ㅣ','ㅐ','ㅔ','ㅘ','ㅝ','ㅢ'];
let cur='ㄱ',curS=0,animT=null,curList=CON,drawDist=0;
const dc=document.getElementById('dc'),dctx=dc.getContext('2d');
const pc=document.getElementById('pc'),pctx=pc.getContext('2d');
const praiseEl=document.getElementById('praise');
const PRAISES=['Gut gemacht! 👏','Toll! ⭐','Super! 🎉','Bravo! 💪','Klasse! ✨','Spitze! 🌟','Wunderbar! 🎯'];
let praiseT=null;
function showPraise(){
  praiseEl.textContent=PRAISES[Math.floor(Math.random()*PRAISES.length)];
  praiseEl.classList.add('show');
  if(praiseT)clearTimeout(praiseT);
  praiseT=setTimeout(()=>{praiseEl.classList.remove('show');},1600);
}
function setMode(m,btn){
  document.querySelectorAll('.mbtn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  curList=m==='c'?CON:VOW;
  const cg=document.getElementById('cg');cg.innerHTML='';
  curList.forEach(ch=>{
    const b=document.createElement('button');
    b.className='cbtn'+(ch===cur?' sel':'');
    b.textContent=ch;b.onclick=()=>selChar(ch);
    cg.appendChild(b);
  });
  updateCharLabel();
}
function selChar(ch){
  cur=ch;curS=0;drawDist=0;if(animT){clearTimeout(animT);animT=null;}
  document.querySelectorAll('.cbtn').forEach(b=>b.classList.toggle('sel',b.textContent===ch));
  document.getElementById('cd').textContent=ch;
  drawD();updateSI();drawGuide();updateCharLabel();
}
function navChar(d){
  const i=curList.indexOf(cur);
  selChar(curList[(i+d+curList.length)%curList.length]);
}
function updateCharLabel(){
  const i=curList.indexOf(cur);
  document.getElementById('cl').textContent=(i+1)+' / '+curList.length;
}
function drawStroke(ctx,sk,color,lw){
  ctx.strokeStyle=color;ctx.lineWidth=lw||9;ctx.lineCap='round';ctx.lineJoin='round';
  if(sk.t==='l'){
    ctx.beginPath();ctx.moveTo(sk.p[0][0],sk.p[0][1]);
    for(let i=1;i<sk.p.length;i++)ctx.lineTo(sk.p[i][0],sk.p[i][1]);
    ctx.stroke();
  } else {
    ctx.beginPath();ctx.arc(sk.cx,sk.cy,sk.r,-Math.PI/2,3*Math.PI/2,true);ctx.stroke();
  }
}
function drawNum(ctx,sk,n,c){
  let x,y;
  if(sk.t==='l'){x=sk.p[0][0];y=sk.p[0][1];}
  else{x=sk.cx;y=sk.cy-sk.r;}
  ctx.fillStyle=c||'#e64980';ctx.beginPath();ctx.arc(x,y,13,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#fff';ctx.font='bold 11px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
  ctx.fillText(String(n),x,y);
}
function drawGhost(ctx,ch,alpha,color){
  ctx.save();ctx.globalAlpha=alpha||0.07;
  ctx.font='bold 162px serif';ctx.fillStyle=color||'#339af0';
  ctx.textAlign='center';ctx.textBaseline='middle';
  ctx.fillText(ch,110,114);ctx.restore();
}
function drawD(){
  const strokes=S[cur]||[];
  dctx.clearRect(0,0,220,220);
  drawGhost(dctx,cur,0.07,'#339af0');
  // faint remaining
  for(let i=curS;i<strokes.length;i++){
    dctx.save();dctx.globalAlpha=0.15;drawStroke(dctx,strokes[i],'#adb5bd',7);dctx.restore();
  }
  // completed
  for(let i=0;i<curS&&i<strokes.length;i++){
    drawStroke(dctx,strokes[i],'#339af0',9);drawNum(dctx,strokes[i],i+1,'#1c7ed6');
  }
  // current
  if(curS<strokes.length){
    drawStroke(dctx,strokes[curS],'#e64980',9);drawNum(dctx,strokes[curS],curS+1,'#e64980');
  }
}
function updateSI(){
  const t=(S[cur]||[]).length;
  document.getElementById('si').textContent=curS>=t?`✅ Fertig! ${t}/${t}`:`Strich ${curS+1}/${t}`;
}
function nextS(){const t=(S[cur]||[]).length;if(curS<t){curS++;drawD();updateSI();}}
function prevS(){if(curS>0){curS--;drawD();updateSI();}}
function resetD(){curS=0;if(animT){clearTimeout(animT);animT=null;}drawD();updateSI();}
function animAll(){
  curS=0;drawD();updateSI();
  const t=(S[cur]||[]).length;
  function step(){if(curS<t){curS++;drawD();updateSI();animT=setTimeout(step,650);}}
  animT=setTimeout(step,350);
}
function drawGuide(){
  pctx.clearRect(0,0,220,220);drawGhost(pctx,cur,0.08,'#51cf66');drawDist=0;
}
function clearP(){drawGuide();}
// Drawing
let drw=false,lx=0,ly=0;
const PRAISE_DIST=180;
function pos(e,cvs){
  const r=cvs.getBoundingClientRect(),sx=cvs.width/r.width,sy=cvs.height/r.height;
  if(e.touches)return{x:(e.touches[0].clientX-r.left)*sx,y:(e.touches[0].clientY-r.top)*sy};
  return{x:(e.clientX-r.left)*sx,y:(e.clientY-r.top)*sy};
}
function addDist(p){
  drawDist+=Math.hypot(p.x-lx,p.y-ly);
  if(drawDist>=PRAISE_DIST){showPraise();drawDist=0;}
}
pc.addEventListener('mousedown',e=>{drw=true;const p=pos(e,pc);lx=p.x;ly=p.y;});
pc.addEventListener('mousemove',e=>{
  if(!drw)return;const p=pos(e,pc);
  pctx.strokeStyle='#2b8a3e';pctx.lineWidth=9;pctx.lineCap='round';
  pctx.beginPath();pctx.moveTo(lx,ly);pctx.lineTo(p.x,p.y);pctx.stroke();
  addDist(p);lx=p.x;ly=p.y;
});
pc.addEventListener('mouseup',()=>drw=false);
pc.addEventListener('mouseleave',()=>drw=false);
pc.addEventListener('touchstart',e=>{e.preventDefault();drw=true;const p=pos(e,pc);lx=p.x;ly=p.y;},{passive:false});
pc.addEventListener('touchmove',e=>{
  e.preventDefault();if(!drw)return;const p=pos(e,pc);
  pctx.strokeStyle='#2b8a3e';pctx.lineWidth=9;pctx.lineCap='round';
  pctx.beginPath();pctx.moveTo(lx,ly);pctx.lineTo(p.x,p.y);pctx.stroke();
  addDist(p);lx=p.x;ly=p.y;
},{passive:false});
pc.addEventListener('touchend',()=>drw=false);
// Swipe navigation between characters (skip if touch starts on practice canvas)
let swipeX=0,swipeY=0;
document.addEventListener('touchstart',e=>{
  if(e.target===pc)return;
  swipeX=e.touches[0].clientX;swipeY=e.touches[0].clientY;
},{passive:true});
document.addEventListener('touchend',e=>{
  if(e.target===pc)return;
  const dx=e.changedTouches[0].clientX-swipeX;
  const dy=e.changedTouches[0].clientY-swipeY;
  if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.5)navChar(dx<0?1:-1);
},{passive:true});
// Init
setMode('c',document.getElementById('btn-con'));selChar('ㄱ');
</script></body></html>"""

    components.html(STROKE_HTML, height=910, scrolling=True)
