"""User identity & device detection.

Strategie (KISS, ohne externe Pakete):
  • URL query param ist die *source of truth* (überlebt reload, shareable)
  • session_state.user_name spiegelt das (single-session cache)
  • localStorage = best-effort backup (iframe sandbox kann es blockieren)
  • Onboarding nutzt KEIN st.form (vermeidet submit-button race condition)
"""
import json
import streamlit as st
import streamlit.components.v1 as components

_STORAGE_KEY = "ko_lernen_user"

_OS_EMOJI = {"iOS": "📱", "Android": "🤖", "Desktop": "💻"}
_OS_LABEL = {"iOS": "iPhone", "Android": "Android", "Desktop": "Desktop"}


# ─────────────────────────────────────────────────────────────────────────────
# JS helpers (best-effort — können bei strikten iframe-sandboxes scheitern)
# ─────────────────────────────────────────────────────────────────────────────
def _detect_os_once() -> None:
    """OS in URL query schreiben (einmalig, falls noch nicht vorhanden)."""
    if st.session_state.get("_os_detected"):
        return
    st.session_state._os_detected = True
    if st.query_params.get("os"):
        return  # bereits gesetzt — nichts tun
    components.html("""
    <script>
    (function(){
        try {
            const url = new URL(window.parent.location.href);
            if (url.searchParams.get('os')) return;
            const ua = navigator.userAgent || '';
            let os = 'Desktop';
            if (/iPhone|iPad|iPod/i.test(ua)) os = 'iOS';
            else if (/Android/i.test(ua))     os = 'Android';
            url.searchParams.set('os', os);
            window.parent.location.replace(url.toString());
        } catch(e) { console.warn('os detect', e); }
    })();
    </script>
    """, height=0)


def _load_name_from_local_storage_once() -> None:
    """Beim Onboarding einmalig versuchen, Name aus localStorage zu laden."""
    if st.session_state.get("_ls_load_tried"):
        return
    st.session_state._ls_load_tried = True
    if st.query_params.get("name"):
        return  # URL hat schon einen Namen
    components.html(f"""
    <script>
    (function(){{
        try {{
            const url = new URL(window.parent.location.href);
            if (url.searchParams.get('name')) return;
            const raw = localStorage.getItem({json.dumps(_STORAGE_KEY)});
            if (!raw) return;
            const data = JSON.parse(raw);
            if (!data.name) return;
            url.searchParams.set('name', data.name);
            window.parent.location.replace(url.toString());
        }} catch(e) {{ console.warn('ls load', e); }}
    }})();
    </script>
    """, height=0)


def _save_to_local_storage(name: str, os_kind: str) -> None:
    payload = json.dumps({"name": name, "os": os_kind})
    components.html(f"""
    <script>
    try {{
        localStorage.setItem({json.dumps(_STORAGE_KEY)}, {json.dumps(payload)});
    }} catch(e) {{}}
    </script>
    """, height=0)


# ─────────────────────────────────────────────────────────────────────────────
# Onboarding CSS
# ─────────────────────────────────────────────────────────────────────────────
def _inject_onboarding_css() -> None:
    if st.session_state.get("_onb_css"):
        return
    st.session_state._onb_css = True
    st.markdown("""
    <style>
    .onb-hero { text-align: center; padding: 2.5rem 1rem 1.4rem; }
    .onb-emoji { font-size: 3.4rem; margin-bottom: .35rem; line-height: 1; }
    .onb-title {
        font-size: 1.55rem; font-weight: 800; margin: 0;
        background: linear-gradient(135deg, #e64980 0%, #845ef7 60%, #339af0 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -.01em;
    }
    .onb-sub { color: #6c757d; font-size: .9rem; margin: .35rem 0 .85rem; }
    .onb-badge {
        display: inline-block;
        background: #f3f0ff; color: #5f3dc4;
        padding: 5px 14px; border-radius: 100px;
        font-size: .78rem; font-weight: 700;
        letter-spacing: .02em;
    }
    .onb-hint {
        font-size: .72rem; color: #adb5bd;
        text-align: center; margin-top: .8rem;
        line-height: 1.5;
    }
    @media (prefers-color-scheme: dark) {
        .onb-sub { color: #adb5bd; }
        .onb-badge { background: #3b2c66; color: #d0bfff; }
        .onb-hint { color: #6c757d; }
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
def get_os() -> str:
    val = (st.query_params.get("os") or "").strip()
    return val if val in ("iOS", "Android", "Desktop") else "Desktop"


def os_emoji(os_kind: str | None = None) -> str:
    return _OS_EMOJI.get(os_kind or get_os(), "💻")


def os_label(os_kind: str | None = None) -> str:
    return _OS_LABEL.get(os_kind or get_os(), "Gerät")


def get_name(fallback: str = "Freund") -> str:
    if name := st.session_state.get("user_name"):
        return name
    qp_name = (st.query_params.get("name") or "").strip()[:30]
    if qp_name:
        st.session_state.user_name = qp_name
        return qp_name
    return fallback


def require_user() -> dict:
    """Gate: liefert {name, os, is_known} oder zeigt Onboarding und stoppt."""
    qp = st.query_params

    # 1) URL query → session_state (auch wenn URL nachträglich gesetzt wurde)
    qp_name = (qp.get("name") or "").strip()[:30]
    if qp_name and st.session_state.get("user_name") != qp_name:
        st.session_state.user_name = qp_name

    # 2) OS detection (best-effort, läuft einmalig pro Session)
    _detect_os_once()

    name    = (st.session_state.get("user_name") or "").strip()
    os_kind = get_os()

    if name:
        # Erstes Durchlaufen nach Submit: URL + localStorage syncen
        if qp.get("name") != name:
            st.query_params["name"] = name
        if not st.session_state.get("_user_persisted"):
            _save_to_local_storage(name, os_kind)
            st.session_state._user_persisted = True
        return {"name": name, "os": os_kind, "is_known": True}

    # 3) Onboarding — KEIN st.form (vermeidet submit-button race)
    _load_name_from_local_storage_once()
    _inject_onboarding_css()

    badge = f"{_OS_EMOJI.get(os_kind, '💻')} {_OS_LABEL.get(os_kind, 'Gerät')}"
    st.markdown(f"""
    <div class="onb-hero">
        <div class="onb-emoji">🇰🇷 👋</div>
        <h2 class="onb-title">안녕하세요!</h2>
        <p class="onb-sub">Schön dass du da bist · 만나서 반가워요</p>
        <div class="onb-badge">{badge}</div>
    </div>
    """, unsafe_allow_html=True)

    # Plain text_input + button (kein form-block, kein auto-rerun-race)
    st.text_input(
        "Dein Vorname",
        placeholder="z.B. Anna, Max, 민준 …",
        label_visibility="collapsed",
        max_chars=30,
        key="onb_name_in",
    )
    clicked = st.button(
        "✨ Loslegen! · 시작하기",
        use_container_width=True,
        type="primary",
        key="onb_submit_btn",
    )

    if clicked:
        # Direkt aus session_state lesen — am robustesten gegen race conditions
        raw = (st.session_state.get("onb_name_in") or "").strip()
        clean = raw[:30]
        if clean:
            st.session_state.user_name = clean
            st.session_state._user_persisted = False
            # URL sofort syncen (überlebt page reload)
            st.query_params["name"] = clean
            st.rerun()
        else:
            st.warning("Bitte gib einen Namen ein. · 이름을 입력해 주세요.")

    st.markdown(
        '<p class="onb-hint">💡 Dein Name wird nur auf deinem Gerät gespeichert.<br>'
        '이름은 이 기기에만 저장됩니다.</p>',
        unsafe_allow_html=True,
    )

    # Debug-Info — hilft beim Diagnostizieren von hängen-bleiben-Schleifen
    with st.expander("🔧 Debug-Info (falls etwas hängt)"):
        st.json({
            "session_state.user_name":  st.session_state.get("user_name"),
            "session_state.onb_name_in": st.session_state.get("onb_name_in"),
            "query.name":               st.query_params.get("name"),
            "query.os":                 st.query_params.get("os"),
            "_os_detected":             st.session_state.get("_os_detected"),
            "_ls_load_tried":           st.session_state.get("_ls_load_tried"),
            "_user_persisted":          st.session_state.get("_user_persisted"),
            "button_clicked_this_run":  clicked,
        })
        if st.button("⚠️ Komplett zurücksetzen (alles vergessen)", key="onb_dbg_reset"):
            clear_user()
            st.rerun()

    st.stop()
    return {"name": "", "os": os_kind, "is_known": False}


def clear_user() -> None:
    """Forget current user (sidebar reset etc.)."""
    for k in (
        "user_name", "_user_persisted", "_ls_load_tried",
        "_os_detected", "_onb_css",
        "onb_name_in", "onb_submit_btn",
    ):
        st.session_state.pop(k, None)
    try:
        del st.query_params["name"]
    except KeyError:
        pass
    components.html(f"""
    <script>
    try {{ localStorage.removeItem({json.dumps(_STORAGE_KEY)}); }} catch(e) {{}}
    </script>
    """, height=0)
