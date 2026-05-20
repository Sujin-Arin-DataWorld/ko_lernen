"""User identity & device detection.

Browser can't read OS-level user name (sandbox), so we:
  1. Detect device class (iPhone / Android / Desktop) via User-Agent
  2. Ask once for a name on first visit
  3. Persist to localStorage → auto-fill on next visit via URL query param
"""
import json
import streamlit as st
import streamlit.components.v1 as components

_STORAGE_KEY = "ko_lernen_user"
_FALLBACK    = "Freund"

_OS_EMOJI = {"iOS": "📱", "Android": "🤖", "Desktop": "💻"}
_OS_LABEL = {"iOS": "iPhone", "Android": "Android", "Desktop": "Desktop"}


def _bootstrap_js() -> None:
    """One-shot JS: detect OS + read localStorage → sync to URL query and reload."""
    if st.session_state.get("_user_boot"):
        return
    st.session_state._user_boot = True
    components.html(f"""
    <script>
    (function(){{
        if (window.parent._koUserBootstrapped) return;
        window.parent._koUserBootstrapped = true;
        try {{
            const url = new URL(window.parent.location.href);
            const ua  = navigator.userAgent || '';
            let os = 'Desktop';
            if (/iPhone|iPad|iPod/i.test(ua)) os = 'iOS';
            else if (/Android/i.test(ua))     os = 'Android';

            let storedName = '';
            try {{
                const raw = localStorage.getItem({json.dumps(_STORAGE_KEY)});
                if (raw) storedName = (JSON.parse(raw).name || '').trim();
            }} catch(e) {{}}

            let changed = false;
            if (url.searchParams.get('os') !== os) {{
                url.searchParams.set('os', os);
                changed = true;
            }}
            if (storedName && url.searchParams.get('name') !== storedName) {{
                url.searchParams.set('name', storedName);
                changed = true;
            }}
            if (changed) window.parent.location.replace(url.toString());
        }} catch(e) {{ console.warn('ko_lernen bootstrap', e); }}
    }})();
    </script>
    """, height=0)


def _persist_to_local_storage(name: str, os_kind: str) -> None:
    payload = json.dumps({"name": name, "os": os_kind})
    components.html(f"""
    <script>
    try {{
        localStorage.setItem({json.dumps(_STORAGE_KEY)}, {json.dumps(payload)});
    }} catch(e) {{}}
    </script>
    """, height=0)


def _inject_onboarding_css() -> None:
    if st.session_state.get("_onb_css"):
        return
    st.session_state._onb_css = True
    st.markdown("""
    <style>
    .onb-hero {
        text-align: center;
        padding: 2.5rem 1rem 1.4rem;
    }
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


def get_os() -> str:
    """'iOS' | 'Android' | 'Desktop'"""
    qp = st.query_params
    val = (qp.get("os") or "").strip()
    return val if val in ("iOS", "Android", "Desktop") else "Desktop"


def os_emoji(os_kind: str | None = None) -> str:
    return _OS_EMOJI.get(os_kind or get_os(), "💻")


def os_label(os_kind: str | None = None) -> str:
    return _OS_LABEL.get(os_kind or get_os(), "Gerät")


def get_name(fallback: str = _FALLBACK) -> str:
    """Current name (session_state → query param → fallback)."""
    name = st.session_state.get("user_name")
    if name:
        return name
    qp_name = (st.query_params.get("name") or "").strip()
    if qp_name:
        st.session_state.user_name = qp_name[:30]
        return st.session_state.user_name
    return fallback


def require_user() -> dict:
    """Onboarding gate. Returns user dict {name, os, is_known} or stops with form."""
    _bootstrap_js()

    qp = st.query_params
    qp_name = (qp.get("name") or "").strip()[:30]
    if qp_name and not st.session_state.get("user_name"):
        st.session_state.user_name = qp_name

    name    = st.session_state.get("user_name", "")
    os_kind = get_os()

    if name:
        return {"name": name, "os": os_kind, "is_known": True}

    # ── Onboarding UI ────────────────────────────────────────────────────────
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

    with st.form("user_name_form", clear_on_submit=False):
        name_in = st.text_input(
            "Dein Vorname",
            placeholder="z.B. Anna, Max, 민준 …",
            label_visibility="collapsed",
            max_chars=30,
            key="onb_name_in",
        )
        if st.form_submit_button("✨ Loslegen! · 시작하기", use_container_width=True, type="primary"):
            clean = name_in.strip()[:30]
            if clean:
                st.session_state.user_name = clean
                st.query_params["name"] = clean
                _persist_to_local_storage(clean, os_kind)
                st.rerun()

    st.markdown(
        '<p class="onb-hint">💡 Dein Name wird nur lokal auf deinem Gerät gespeichert.<br>'
        '이름은 이 기기에만 저장됩니다.</p>',
        unsafe_allow_html=True,
    )
    st.stop()
    return {"name": "", "os": os_kind, "is_known": False}


def clear_user() -> None:
    """Forget current user (sidebar reset etc.)."""
    for k in ("user_name", "_user_boot", "onb_name_in"):
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
