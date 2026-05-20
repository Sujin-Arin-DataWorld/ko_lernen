"""🔤 Hangul-Übung — Das koreanische Alphabet"""
import random, sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

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

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Übersicht", "자음 Konsonanten", "모음 Vokale", "🃏 Karten-Übung", "✍️ Schreiben"])

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
.char-grid{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:14px;max-height:140px;overflow-y:auto;padding:4px}
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
    <canvas id="pc" width="220" height="220"></canvas>
    <button class="clrbtn" onclick="clearP()">🗑 Löschen</button>
  </div>
</div>
<script>
const S={
 'ㄱ':[{t:'l',p:[[28,62],[162,62]]},{t:'l',p:[[162,62],[162,175]]}],
 'ㄴ':[{t:'l',p:[[45,30],[45,162]]},{t:'l',p:[[45,162],[175,162]]}],
 'ㄷ':[{t:'l',p:[[28,42],[165,42]]},{t:'l',p:[[28,42],[28,162]]},{t:'l',p:[[28,162],[165,162]]}],
 'ㄹ':[{t:'l',p:[[28,40],[162,40]]},{t:'l',p:[[28,40],[28,102]]},{t:'l',p:[[28,102],[162,102]]},{t:'l',p:[[162,102],[162,162]]},{t:'l',p:[[28,162],[162,162]]}],
 'ㅁ':[{t:'l',p:[[28,40],[162,40]]},{t:'l',p:[[28,40],[28,162]]},{t:'l',p:[[162,40],[162,162]]},{t:'l',p:[[28,162],[162,162]]}],
 'ㅂ':[{t:'l',p:[[68,40],[68,162]]},{t:'l',p:[[152,40],[152,162]]},{t:'l',p:[[68,40],[152,40]]},{t:'l',p:[[68,101],[152,101]]},{t:'l',p:[[68,162],[152,162]]}],
 'ㅅ':[{t:'l',p:[[110,38],[42,168]]},{t:'l',p:[[110,38],[178,168]]}],
 'ㅇ':[{t:'a',cx:110,cy:112,r:62,st:-Math.PI/2,en:Math.PI*3/2}],
 'ㅈ':[{t:'l',p:[[25,58],[195,58]]},{t:'l',p:[[110,58],[45,170]]},{t:'l',p:[[110,58],[175,170]]}],
 'ㅊ':[{t:'l',p:[[80,24],[140,24]]},{t:'l',p:[[25,65],[195,65]]},{t:'l',p:[[110,65],[45,172]]},{t:'l',p:[[110,65],[175,172]]}],
 'ㅋ':[{t:'l',p:[[25,50],[165,50]]},{t:'l',p:[[25,108],[152,108]]},{t:'l',p:[[165,50],[165,175]]}],
 'ㅌ':[{t:'l',p:[[25,40],[165,40]]},{t:'l',p:[[25,40],[25,165]]},{t:'l',p:[[25,101],[165,101]]},{t:'l',p:[[25,165],[165,165]]}],
 'ㅍ':[{t:'l',p:[[22,68],[195,68]]},{t:'l',p:[[22,160],[195,160]]},{t:'l',p:[[78,68],[78,160]]},{t:'l',p:[[140,68],[140,160]]}],
 'ㅎ':[{t:'l',p:[[78,22],[142,22]]},{t:'l',p:[[110,22],[110,48]]},{t:'a',cx:110,cy:118,r:58,st:-Math.PI/2,en:Math.PI*3/2}],
 'ㄲ':[{t:'l',p:[[15,62],[90,62]]},{t:'l',p:[[90,62],[90,172]]},{t:'l',p:[[100,62],[175,62]]},{t:'l',p:[[175,62],[175,172]]}],
 'ㄸ':[{t:'l',p:[[12,42],[96,42]]},{t:'l',p:[[12,42],[12,162]]},{t:'l',p:[[12,162],[96,162]]},{t:'l',p:[[106,42],[195,42]]},{t:'l',p:[[106,42],[106,162]]},{t:'l',p:[[106,162],[195,162]]}],
 'ㅃ':[{t:'l',p:[[12,40],[55,40]]},{t:'l',p:[[12,40],[12,162]]},{t:'l',p:[[55,40],[55,162]]},{t:'l',p:[[12,101],[55,101]]},{t:'l',p:[[12,162],[55,162]]},{t:'l',p:[[65,40],[108,40]]},{t:'l',p:[[65,40],[65,162]]},{t:'l',p:[[108,40],[108,162]]},{t:'l',p:[[65,101],[108,101]]},{t:'l',p:[[65,162],[108,162]]}],
 'ㅆ':[{t:'l',p:[[70,38],[30,162]]},{t:'l',p:[[70,38],[110,162]]},{t:'l',p:[[148,38],[108,162]]},{t:'l',p:[[148,38],[188,162]]}],
 'ㅉ':[{t:'l',p:[[12,58],[108,58]]},{t:'l',p:[[60,58],[22,168]]},{t:'l',p:[[60,58],[98,168]]},{t:'l',p:[[112,58],[208,58]]},{t:'l',p:[[160,58],[122,168]]},{t:'l',p:[[160,58],[198,168]]}],
 'ㅏ':[{t:'l',p:[[100,25],[100,195]]},{t:'l',p:[[100,110],[168,110]]}],
 'ㅑ':[{t:'l',p:[[100,25],[100,195]]},{t:'l',p:[[100,75],[168,75]]},{t:'l',p:[[100,135],[168,135]]}],
 'ㅓ':[{t:'l',p:[[110,25],[110,195]]},{t:'l',p:[[42,110],[110,110]]}],
 'ㅕ':[{t:'l',p:[[110,25],[110,195]]},{t:'l',p:[[42,75],[110,75]]},{t:'l',p:[[42,135],[110,135]]}],
 'ㅗ':[{t:'l',p:[[22,100],[195,100]]},{t:'l',p:[[108,100],[108,185]]}],
 'ㅛ':[{t:'l',p:[[22,100],[195,100]]},{t:'l',p:[[72,100],[72,185]]},{t:'l',p:[[145,100],[145,185]]}],
 'ㅜ':[{t:'l',p:[[22,110],[195,110]]},{t:'l',p:[[108,25],[108,110]]}],
 'ㅠ':[{t:'l',p:[[22,110],[195,110]]},{t:'l',p:[[72,25],[72,110]]},{t:'l',p:[[145,25],[145,110]]}],
 'ㅡ':[{t:'l',p:[[22,110],[195,110]]}],
 'ㅣ':[{t:'l',p:[[110,25],[110,195]]}],
 'ㅐ':[{t:'l',p:[[78,25],[78,195]]},{t:'l',p:[[78,110],[145,110]]},{t:'l',p:[[145,25],[145,195]]}],
 'ㅔ':[{t:'l',p:[[78,25],[78,195]]},{t:'l',p:[[42,110],[78,110]]},{t:'l',p:[[145,25],[145,195]]}],
 'ㅘ':[{t:'l',p:[[22,100],[95,100]]},{t:'l',p:[[58,100],[58,185]]},{t:'l',p:[[95,25],[95,195]]},{t:'l',p:[[95,110],[165,110]]}],
 'ㅝ':[{t:'l',p:[[22,110],[95,110]]},{t:'l',p:[[58,25],[58,110]]},{t:'l',p:[[95,25],[95,195]]},{t:'l',p:[[35,110],[95,110]]}],
 'ㅢ':[{t:'l',p:[[22,110],[195,110]]},{t:'l',p:[[108,25],[108,195]]}],
};
const CON=['ㄱ','ㄴ','ㄷ','ㄹ','ㅁ','ㅂ','ㅅ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ','ㄲ','ㄸ','ㅃ','ㅆ','ㅉ'];
const VOW=['ㅏ','ㅑ','ㅓ','ㅕ','ㅗ','ㅛ','ㅜ','ㅠ','ㅡ','ㅣ','ㅐ','ㅔ','ㅘ','ㅝ','ㅢ'];
let cur='ㄱ',curS=0,animT=null;
const dc=document.getElementById('dc'),dctx=dc.getContext('2d');
const pc=document.getElementById('pc'),pctx=pc.getContext('2d');

function setMode(m,btn){
  document.querySelectorAll('.mbtn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  const cg=document.getElementById('cg');cg.innerHTML='';
  (m==='c'?CON:VOW).forEach(ch=>{
    const b=document.createElement('button');
    b.className='cbtn'+(ch===cur?' sel':'');
    b.textContent=ch;b.onclick=()=>selChar(ch);
    cg.appendChild(b);
  });
}
function selChar(ch){
  cur=ch;curS=0;if(animT){clearTimeout(animT);animT=null;}
  document.querySelectorAll('.cbtn').forEach(b=>b.classList.toggle('sel',b.textContent===ch));
  document.getElementById('cd').textContent=ch;
  drawD();updateSI();drawGuide();
}
function drawStroke(ctx,sk,color,lw){
  ctx.strokeStyle=color;ctx.lineWidth=lw||9;ctx.lineCap='round';ctx.lineJoin='round';
  if(sk.t==='l'){
    ctx.beginPath();ctx.moveTo(sk.p[0][0],sk.p[0][1]);
    for(let i=1;i<sk.p.length;i++)ctx.lineTo(sk.p[i][0],sk.p[i][1]);
    ctx.stroke();
  } else {
    ctx.beginPath();ctx.arc(sk.cx,sk.cy,sk.r,sk.st,sk.en,false);ctx.stroke();
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
  pctx.clearRect(0,0,220,220);drawGhost(pctx,cur,0.08,'#51cf66');
}
function clearP(){drawGuide();}
// Drawing
let drw=false,lx=0,ly=0;
function pos(e,cvs){
  const r=cvs.getBoundingClientRect(),sx=cvs.width/r.width,sy=cvs.height/r.height;
  if(e.touches)return{x:(e.touches[0].clientX-r.left)*sx,y:(e.touches[0].clientY-r.top)*sy};
  return{x:(e.clientX-r.left)*sx,y:(e.clientY-r.top)*sy};
}
pc.addEventListener('mousedown',e=>{drw=true;const p=pos(e,pc);lx=p.x;ly=p.y;});
pc.addEventListener('mousemove',e=>{
  if(!drw)return;const p=pos(e,pc);
  pctx.strokeStyle='#2b8a3e';pctx.lineWidth=9;pctx.lineCap='round';
  pctx.beginPath();pctx.moveTo(lx,ly);pctx.lineTo(p.x,p.y);pctx.stroke();
  lx=p.x;ly=p.y;
});
pc.addEventListener('mouseup',()=>drw=false);
pc.addEventListener('mouseleave',()=>drw=false);
pc.addEventListener('touchstart',e=>{e.preventDefault();drw=true;const p=pos(e,pc);lx=p.x;ly=p.y;},{passive:false});
pc.addEventListener('touchmove',e=>{
  e.preventDefault();if(!drw)return;const p=pos(e,pc);
  pctx.strokeStyle='#2b8a3e';pctx.lineWidth=9;pctx.lineCap='round';
  pctx.beginPath();pctx.moveTo(lx,ly);pctx.lineTo(p.x,p.y);pctx.stroke();
  lx=p.x;ly=p.y;
},{passive:false});
pc.addEventListener('touchend',()=>drw=false);
// Init
setMode('c',document.getElementById('btn-con'));selChar('ㄱ');
</script></body></html>"""

    components.html(STROKE_HTML, height=860, scrolling=True)
