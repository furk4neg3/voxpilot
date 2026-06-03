"""
VoxPilot — TTS Studio
Streamlit Frontend Application

A polished, professional Streamlit interface for text-to-speech generation,
run metadata, evaluation dashboards, and metrics tracking.
"""

import os
import time
import datetime
from typing import Optional

import requests
import streamlit as st
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASE_URL = os.getenv("VOXPILOT_API_URL", "http://localhost:8000")

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="VoxPilot - TTS Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f4f6fa;
    --bg-accent: #eef2ff;
    --surface: #ffffff;
    --surface-muted: #f8fafc;
    --surface-elevated: #ffffff;
    --ink: #0f172a;
    --ink-secondary: #334155;
    --muted: #64748b;
    --muted-light: #94a3b8;
    --border: #e2e8f0;
    --border-strong: #cbd5e1;
    --primary: #4f46e5;
    --primary-hover: #4338ca;
    --primary-soft: #eef2ff;
    --accent: #0ea5e9;
    --accent-soft: #e0f2fe;
    --success: #059669;
    --success-soft: #ecfdf5;
    --danger: #dc2626;
    --danger-soft: #fef2f2;
    --warning: #d97706;
    --warning-soft: #fffbeb;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.04);
    --shadow-sm: 0 4px 12px rgba(15, 23, 42, 0.05);
    --shadow-md: 0 12px 32px rgba(15, 23, 42, 0.07);
    --shadow-lg: 0 24px 48px rgba(15, 23, 42, 0.08);
    --transition: 0.18s cubic-bezier(0.4, 0, 0.2, 1);
}

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    color: var(--ink);
    -webkit-font-smoothing: antialiased;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(79, 70, 229, 0.12), transparent),
        radial-gradient(ellipse 60% 40% at 100% 0%, rgba(14, 165, 233, 0.08), transparent),
        var(--bg);
}

[data-testid="stMainBlockContainer"] {
    max-width: 1180px;
    padding: 1.5rem 1.75rem 2.5rem;
}

#MainMenu, footer, header { visibility: hidden; }

/* ── App shell ─────────────────────────────────────────────────────── */
.vp-shell {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-lg);
    overflow: hidden;
    margin-bottom: 1.5rem;
}

.vp-shell-bar {
    height: 3px;
    background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 50%, #818cf8 100%);
}

.vp-shell-body {
    padding: 1.75rem 1.85rem 1.5rem;
}

/* ── Header ──────────────────────────────────────────────────────────── */
.vp-header {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    gap: 1.25rem 1.75rem;
    align-items: center;
    padding-bottom: 1.35rem;
    margin-bottom: 0.25rem;
    border-bottom: 1px solid var(--border);
}

.vp-logo {
    width: 52px;
    height: 52px;
    border-radius: var(--radius-md);
    background: linear-gradient(135deg, var(--primary) 0%, #6366f1 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.45rem;
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.28);
    flex-shrink: 0;
}

.vp-kicker {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--primary);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}

.vp-kicker-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent);
}

.vp-header h1 {
    color: var(--ink);
    font-size: clamp(1.65rem, 3.5vw, 2.15rem);
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.02em;
    line-height: 1.15;
}

.vp-header .subtitle {
    max-width: 560px;
    color: var(--muted);
    font-size: 0.92rem;
    font-weight: 500;
    line-height: 1.55;
    margin: 0.45rem 0 0;
}

.vp-status-panel {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 0.5rem;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    min-height: 32px;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: var(--surface-muted);
    color: var(--ink-secondary);
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
}

.status-online {
    border-color: rgba(5, 150, 105, 0.25);
    color: var(--success);
    background: var(--success-soft);
}

.status-offline {
    border-color: rgba(220, 38, 38, 0.22);
    color: var(--danger);
    background: var(--danger-soft);
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: currentColor;
    flex-shrink: 0;
}

.status-dot.green { box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.2); }
.status-dot.red { box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.18); }

/* ── Typography ──────────────────────────────────────────────────────── */
.section-heading {
    color: var(--ink);
    font-size: 0.82rem;
    font-weight: 700;
    margin: 0 0 0.55rem;
    letter-spacing: 0.01em;
}

.vp-section-eyebrow {
    color: var(--primary);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 0 0 0.3rem;
}

.vp-section-title {
    color: var(--ink);
    font-size: 1.22rem;
    font-weight: 800;
    line-height: 1.3;
    margin: 0 0 0.3rem;
    letter-spacing: -0.01em;
}

.vp-section-copy {
    color: var(--muted);
    font-size: 0.875rem;
    line-height: 1.6;
    margin: 0 0 1.15rem;
}

.vp-section-header {
    margin-bottom: 0.25rem;
}

.vp-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.1rem 0;
}

.vp-panel {
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.35rem;
    margin-bottom: 0.5rem;
}

.vp-panel-output {
    background: linear-gradient(180deg, var(--surface) 0%, var(--surface-muted) 100%);
    min-height: 420px;
}

.vp-panel-label {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.85rem;
}

.vp-panel-label-icon {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    background: var(--primary-soft);
    color: var(--primary);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
}

.vp-filter-toolbar {
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 0.85rem 1rem 0.35rem;
    margin-bottom: 1rem;
}

.vp-filter-toolbar-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 0 0 0.65rem;
}

.vp-metrics-group {
    margin-bottom: 0.35rem;
}

.vp-metrics-group-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted-light);
    margin: 0 0 0.75rem;
    padding-left: 0.15rem;
}

/* ── Streamlit controls ──────────────────────────────────────────────── */
[data-testid="stForm"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    background: var(--surface) !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 1.1rem 1.2rem 1.2rem !important;
}

[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    background: var(--surface) !important;
    box-shadow: var(--shadow-xs) !important;
}

[data-testid="stExpander"] summary {
    font-weight: 700 !important;
    color: var(--ink-secondary) !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}

textarea,
input,
[data-baseweb="select"] > div,
[data-baseweb="textarea"] textarea {
    border-radius: var(--radius-sm) !important;
    border-color: var(--border) !important;
    background-color: var(--surface) !important;
    font-family: inherit !important;
}

textarea:focus,
input:focus,
[data-baseweb="select"] > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.14) !important;
}

label, .stSlider label, [data-testid="stWidgetLabel"] p {
    font-weight: 600 !important;
    color: var(--ink-secondary) !important;
    font-size: 0.84rem !important;
}

[data-testid="stFormSubmitButton"] > button,
[data-testid="stButton"] > button {
    border-radius: var(--radius-sm) !important;
    font-weight: 700 !important;
    font-family: inherit !important;
    transition: transform var(--transition), box-shadow var(--transition), background var(--transition) !important;
}

[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, var(--primary) 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    border: none !important;
    padding: 0.7rem 1.15rem !important;
    min-height: 46px !important;
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.28) !important;
}

[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 28px rgba(79, 70, 229, 0.34) !important;
}

[data-testid="stButton"] > button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--ink-secondary) !important;
    min-height: 40px !important;
}

[data-testid="stButton"] > button:hover {
    border-color: var(--border-strong) !important;
    background: var(--surface-muted) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stButton"] > button[kind="primary"] {
    background: var(--primary) !important;
    border-color: var(--primary) !important;
    color: #fff !important;
}

/* Tabs */
[data-testid="stTabs"] {
    margin-top: 0.5rem;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0.25rem;
    border-bottom: 0;
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 0.3rem;
    margin: 0 0 1.35rem;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: var(--radius-sm);
    color: var(--muted);
    font-weight: 700;
    font-size: 0.875rem;
    min-height: 40px;
    padding: 0.45rem 1.15rem;
    transition: color var(--transition), background var(--transition);
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: var(--ink-secondary);
}

[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--primary) !important;
    box-shadow: var(--shadow-sm);
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    display: none;
}

[data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    font-size: 0.875rem !important;
}

/* ── Cards & states ──────────────────────────────────────────────────── */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.05rem 1.15rem;
    min-height: 108px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: var(--shadow-xs);
    transition: border-color var(--transition), box-shadow var(--transition), transform var(--transition);
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: var(--border);
    border-radius: 3px 0 0 3px;
}

.metric-card:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-sm);
    transform: translateY(-1px);
}

.metric-card.vp-metric-primary::before { background: var(--primary); }
.metric-card.vp-metric-accent::before { background: var(--accent); }
.metric-card.vp-metric-success::before { background: var(--success); }
.metric-card.vp-metric-warning::before { background: var(--warning); }
.metric-card.vp-metric-danger::before { background: var(--danger); }

.metric-card .metric-label {
    color: var(--muted);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    line-height: 1.2;
    margin-bottom: 0.4rem;
    text-transform: uppercase;
}

.metric-card .metric-value {
    color: var(--ink);
    font-size: clamp(1.25rem, 2vw, 1.7rem);
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.metric-card .metric-value.accent { color: var(--primary); }
.metric-card .metric-value.secondary { color: var(--accent); }
.metric-card .metric-value.warning { color: var(--warning); }
.metric-card .metric-value.danger { color: var(--danger); }

.vp-card-accent::before { background: var(--primary) !important; }
.vp-card-secondary::before { background: var(--accent) !important; }

.audio-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1.1rem;
    margin: 0.5rem 0 1rem;
    box-shadow: var(--shadow-xs);
}

.audio-container-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.65rem;
}

.vp-empty-state {
    border: 1.5px dashed var(--border-strong);
    border-radius: var(--radius-lg);
    background: var(--surface);
    padding: 2rem 1.5rem;
    color: var(--muted);
    min-height: 280px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 0.65rem;
}

.vp-empty-icon {
    width: 56px;
    height: 56px;
    border-radius: var(--radius-md);
    background: var(--primary-soft);
    color: var(--primary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 0.35rem;
}

.vp-empty-state strong {
    color: var(--ink);
    font-size: 1rem;
    font-weight: 700;
}

.vp-empty-state span {
    max-width: 320px;
    font-size: 0.875rem;
    line-height: 1.55;
}

.vp-note {
    background: var(--warning-soft);
    border: 1px solid #fde68a;
    border-radius: var(--radius-md);
    padding: 0.95rem 1.05rem;
    color: #92400e;
}

.vp-note h4 {
    margin: 0 0 0.3rem;
    font-size: 0.9rem;
    font-weight: 700;
    color: #78350f;
}

.vp-note p {
    color: #92400e;
    font-size: 0.84rem;
    line-height: 1.55;
    margin: 0;
}

.char-counter-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-top: -0.35rem;
    margin-bottom: 0.55rem;
}

.char-progress {
    flex: 1;
    height: 4px;
    background: var(--border);
    border-radius: 999px;
    overflow: hidden;
    max-width: 120px;
}

.char-progress-fill {
    height: 100%;
    border-radius: 999px;
    background: var(--primary);
    transition: width 0.2s ease, background 0.2s ease;
}

.char-progress-fill.warn { background: var(--warning); }
.char-progress-fill.over { background: var(--danger); }

.char-counter {
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
}

.char-counter.ok { color: var(--muted); }
.char-counter.warn { color: var(--warning); }
.char-counter.over { color: var(--danger); }

.vp-evaluation-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 0.25rem 0;
    margin-top: 0.5rem;
}

.vp-footer {
    text-align: center;
    padding: 1.75rem 0 0.25rem;
    margin-top: 1.5rem;
    color: var(--muted-light);
    border-top: 1px solid var(--border);
}

.vp-footer p {
    font-size: 0.78rem;
    margin: 0.15rem 0;
    font-weight: 500;
}

.vp-footer-brand {
    color: var(--muted);
    font-weight: 700;
}

/* ── Responsive ──────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    [data-testid="stMainBlockContainer"] {
        padding: 1rem 0.85rem 2rem;
    }

    .vp-shell-body {
        padding: 1.25rem 1rem 1rem;
    }

    .vp-header {
        grid-template-columns: auto 1fr;
        grid-template-rows: auto auto;
    }

    .vp-status-panel {
        grid-column: 1 / -1;
        justify-content: flex-start;
    }

    .vp-panel {
        padding: 1rem;
    }

    .vp-panel-output {
        min-height: auto;
        margin-top: 0.75rem;
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        overflow-x: auto;
        flex-wrap: nowrap;
    }

    [data-testid="stTabs"] [data-baseweb="tab"] {
        padding: 0.4rem 0.75rem;
        font-size: 0.82rem;
        white-space: nowrap;
    }

    .metric-card {
        min-height: 92px;
        margin-bottom: 0.5rem;
    }

    .vp-empty-state {
        min-height: 200px;
        padding: 1.5rem 1rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------


def api_get(endpoint: str, params: Optional[dict] = None, timeout: int = 10) -> dict:
    """Perform a GET request to the backend."""
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"_error": "Cannot reach backend. Is the server running?"}
    except requests.exceptions.Timeout:
        return {"_error": "Request timed out. The server may be overloaded."}
    except requests.exceptions.HTTPError as exc:
        return {"_error": f"Server returned {exc.response.status_code}"}
    except Exception as exc:
        return {"_error": str(exc)}


def api_post_synthesize(
    text: str,
    language: str,
    voice: str,
    style: str = "neutral",
) -> dict:
    """POST to /synthesize with form data."""
    try:
        data = {
            "text": text,
            "language": language,
            "voice": voice,
            "style": style,
        }
        r = requests.post(f"{API_BASE_URL}/synthesize", data=data, timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot reach backend. Is the server running?"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Synthesis timed out. Try shorter text."}
    except requests.exceptions.HTTPError as exc:
        try:
            body = exc.response.json()
            return {"success": False, "error": body.get("detail", str(exc))}
        except Exception:
            return {"success": False, "error": f"Server error ({exc.response.status_code})"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def api_post_feedback(
    run_id: str,
    rating: int,
    naturalness: Optional[int],
    clarity: Optional[int],
    latency_acceptability: Optional[bool],
    comment: str,
) -> dict:
    """POST generation feedback to the backend."""
    payload = {
        "run_id": run_id,
        "rating": rating,
        "naturalness": naturalness,
        "clarity": clarity,
        "latency_acceptability": latency_acceptability,
        "comment": comment.strip() or None,
    }
    try:
        r = requests.post(f"{API_BASE_URL}/feedback", json=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot reach backend. Is the server running?"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Feedback submission timed out."}
    except requests.exceptions.HTTPError as exc:
        try:
            body = exc.response.json()
            return {"success": False, "error": body.get("detail", str(exc))}
        except Exception:
            return {"success": False, "error": f"Server error ({exc.response.status_code})"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

if "synthesis_result" not in st.session_state:
    st.session_state.synthesis_result = None
if "feedback_submitted_for" not in st.session_state:
    st.session_state.feedback_submitted_for = None
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True


# ---------------------------------------------------------------------------
# Fetch health / voices (cached short-term)
# ---------------------------------------------------------------------------


@st.cache_data(ttl=15)
def fetch_health() -> dict:
    return api_get("/health")


@st.cache_data(ttl=60)
def fetch_voices() -> dict:
    return api_get("/voices")


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

health = fetch_health()
is_online = "_error" not in health

if is_online:
    engine_name = health.get("engine", "Unknown")
    version = health.get("version", "—")
    status_html = f"""
    <span class="status-badge status-online"><span class="status-dot green"></span>Connected</span>
    <span class="status-badge">Engine: {engine_name}</span>
    <span class="status-badge">v{version}</span>
    """
else:
    status_html = """
    <span class="status-badge status-offline"><span class="status-dot red"></span>Disconnected</span>
    """

st.markdown(
    f"""
<div class="vp-shell">
    <div class="vp-shell-bar"></div>
    <div class="vp-shell-body">
        <div class="vp-header">
            <div class="vp-logo">🎙️</div>
            <div>
                <div class="vp-kicker"><span class="vp-kicker-dot"></span> VoxPilot</div>
                <h1>TTS Studio</h1>
                <p class="subtitle">Speech generation workspace with run history, latency metrics, cache visibility, and evaluation feedback.</p>
            </div>
            <div class="vp-status-panel">
                {status_html}
            </div>
        </div>
""",
    unsafe_allow_html=True,
)

if is_online and "fallback-tone" in health.get("engine", ""):
    st.warning(
        "The API is using the tone fallback engine, so generated audio will be beeps instead of speech. "
        "Restart the API with VOXPILOT_ENGINE=system on macOS, or install SpeechT5 dependencies and use VOXPILOT_ENGINE=speecht5.",
        icon="⚠️",
    )


# ---------------------------------------------------------------------------
# Service Notes
# ---------------------------------------------------------------------------

expanded = st.session_state.first_visit
with st.expander("Service Notes", expanded=expanded):
    st.markdown(
        """
<div class="vp-note">
    <h4>Local PoC Runtime</h4>
    <p>Run records are stored locally, process metrics reset on API restart, and the selected engine determines whether output is spoken audio or fallback tones.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    if st.session_state.first_visit:
        st.session_state.first_visit = False


# ---------------------------------------------------------------------------
# Fetch available voices
# ---------------------------------------------------------------------------

voices_data = fetch_voices()
voices_error = "_error" in voices_data

if voices_error:
    voice_list = []
    language_options = ["en"]
    voice_options = ["default"]
else:
    voice_list = voices_data.get("voices", [])
    language_options = sorted(list({v.get("language", "en") for v in voice_list})) or ["en"]
    voice_options = [v.get("id", v.get("name", "default")) for v in voice_list] or ["default"]


# Build voice display map: id -> descriptive label
voice_display_map = {}
for v in voice_list:
    vid = v.get("id", v.get("name", "default"))
    name = v.get("name", vid)
    gender = v.get("gender", "")
    lang = v.get("language", "")
    desc = f"{name}"
    if gender:
        desc += f"  ·  {gender.capitalize()}"
    if lang:
        desc += f"  ·  {lang.upper()}"
    voice_display_map[vid] = desc


# ---------------------------------------------------------------------------
# Main tabs
# ---------------------------------------------------------------------------

tab_generate, tab_dashboard, tab_metrics = st.tabs(["Generate", "History", "Metrics"])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — Generate
# ═══════════════════════════════════════════════════════════════════════════

with tab_generate:
    gen_left, gen_right = st.columns([1.06, 0.94], gap="large")

    with gen_left:
        st.markdown(
            """
<div class="vp-panel">
    <div class="vp-panel-label"><span class="vp-panel-label-icon">✎</span> Compose</div>
    <div class="vp-section-header">
        <p class="vp-section-eyebrow">Input</p>
        <h2 class="vp-section-title">Generation Request</h2>
        <p class="vp-section-copy">Enter the script, choose a language and voice preset, then generate speech through the active backend service.</p>
    </div>
""",
            unsafe_allow_html=True,
        )
        with st.form("synthesis_form", clear_on_submit=False):
            st.markdown('<p class="section-heading">Text Input</p>', unsafe_allow_html=True)
            text_input = st.text_area(
                "Enter text to synthesize",
                height=190,
                max_chars=1000,
                placeholder="e.g. Welcome to VoxPilot, a TTS Studio for speech generation workflows and latency-aware evaluation.",
                label_visibility="collapsed",
            )
            char_count = len(text_input)
            if char_count > 950:
                cc_class = "over" if char_count > 1000 else "warn"
            else:
                cc_class = "ok"
            pct = min(char_count / 1000 * 100, 100)
            st.markdown(
                f"""<div class="char-counter-wrap">
                    <div class="char-progress"><div class="char-progress-fill {cc_class}" style="width:{pct}%"></div></div>
                    <span class="char-counter {cc_class}">{char_count} / 1,000</span>
                </div>""",
                unsafe_allow_html=True,
            )

            st.markdown('<div class="vp-divider"></div>', unsafe_allow_html=True)

            col_lang, col_voice = st.columns(2)
            with col_lang:
                st.markdown('<p class="section-heading">Language</p>', unsafe_allow_html=True)
                default_lang_idx = language_options.index("en") if "en" in language_options else 0
                selected_language = st.selectbox(
                    "Language",
                    options=language_options,
                    index=default_lang_idx,
                    label_visibility="collapsed",
                )

            with col_voice:
                st.markdown('<p class="section-heading">Voice Preset</p>', unsafe_allow_html=True)
                filtered_voices = [
                    v.get("id", v.get("name", "default"))
                    for v in voice_list
                    if v.get("language", "en") == selected_language
                ] or voice_options
                selected_voice = st.selectbox(
                    "Voice",
                    options=filtered_voices,
                    format_func=lambda x: voice_display_map.get(x, x),
                    label_visibility="collapsed",
                )

            st.markdown('<div class="vp-divider"></div>', unsafe_allow_html=True)
            submitted = st.form_submit_button("Generate Speech", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            if not text_input.strip():
                st.error("Please enter some text to synthesize.")
            elif not is_online:
                st.error("Backend is not reachable. Please start the server first.")
            else:
                with st.spinner("Generating speech..."):
                    result = api_post_synthesize(
                        text=text_input.strip(),
                        language=selected_language,
                        voice=selected_voice,
                    )
                    st.session_state.synthesis_result = result
                    st.session_state.feedback_submitted_for = None

    with gen_right:
        result = st.session_state.synthesis_result
        st.markdown(
            """
<div class="vp-panel vp-panel-output">
    <div class="vp-panel-label"><span class="vp-panel-label-icon">▶</span> Output</div>
    <div class="vp-section-header">
        <p class="vp-section-eyebrow">Result</p>
        <h2 class="vp-section-title">Latest Generation</h2>
        <p class="vp-section-copy">Playback, inspect run metadata, and collect evaluator feedback after a successful request.</p>
    </div>
""",
            unsafe_allow_html=True,
        )

        if result is None:
            st.markdown(
                """
<div class="vp-empty-state">
    <div class="vp-empty-icon">🔊</div>
    <strong>No generation yet</strong>
    <span>Your latest result will appear here with playback, latency, cache status, run details, and feedback controls.</span>
</div>
""",
                unsafe_allow_html=True,
            )
        elif result.get("success"):
            audio_url = result.get("audio_url", "")
            if audio_url:
                full_audio_url = (
                    audio_url if audio_url.startswith("http") else f"{API_BASE_URL}{audio_url}"
                )
                st.markdown(
                    '<div class="audio-container"><div class="audio-container-header">🎧 Audio Playback</div>',
                    unsafe_allow_html=True,
                )
                try:
                    audio_data = requests.get(full_audio_url, timeout=10).content
                    st.audio(audio_data, format="audio/wav")
                except Exception:
                    st.warning("Could not load audio for playback.")
                st.markdown("</div>", unsafe_allow_html=True)

            latency = result.get("latency_ms", 0)
            duration = result.get("audio_duration_seconds", 0)
            rtf = result.get("real_time_factor")
            rtf_display = f"{rtf:.2f}" if isinstance(rtf, (int, float)) else "—"
            cache = result.get("cache_hit", False)
            cache_label = "Hit" if cache else "Miss"

            m1, m2 = st.columns(2)
            with m1:
                st.markdown(
                    f"""<div class="metric-card vp-metric-primary">
                        <div class="metric-label">Latency</div>
                        <div class="metric-value accent">{latency:.0f}<span style="font-size:0.85rem;font-weight:600;"> ms</span></div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with m2:
                st.markdown(
                    f"""<div class="metric-card vp-metric-accent">
                        <div class="metric-label">Duration</div>
                        <div class="metric-value secondary">{duration:.2f}<span style="font-size:0.85rem;font-weight:600;"> s</span></div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            m3, m4 = st.columns(2)
            with m3:
                st.markdown(
                    f"""<div class="metric-card">
                        <div class="metric-label">Real-Time Factor</div>
                        <div class="metric-value">{rtf_display}<span style="font-size:0.85rem;font-weight:600;">x</span></div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with m4:
                st.markdown(
                    f"""<div class="metric-card {'vp-metric-success' if cache else ''}">
                        <div class="metric-label">Cache</div>
                        <div class="metric-value {'secondary' if cache else ''}">{cache_label}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            with st.expander("Run Details"):
                detail_cols = st.columns(2)
                with detail_cols[0]:
                    st.markdown(f"**Run ID:** `{result.get('run_id', '—')}`")
                    st.markdown(f"**Engine:** `{result.get('engine', '—')}`")
                    st.markdown(f"**Voice:** `{result.get('voice', '—')}`")
                with detail_cols[1]:
                    st.markdown(f"**Language:** `{result.get('language', '—')}`")
                    st.markdown(f"**Cache Hit:** `{result.get('cache_hit', False)}`")
                    st.markdown(f"**Duration:** `{duration:.2f}s`")
                st.markdown(f"**Audio Path:** `{result.get('audio_path', '—')}`")

            run_id = result.get("run_id")
            if run_id:
                st.markdown(
                    '<div class="vp-evaluation-box"><p class="section-heading" style="padding:0 1.2rem;margin-top:0.85rem;">Evaluation</p>',
                    unsafe_allow_html=True,
                )
                if st.session_state.feedback_submitted_for == run_id:
                    st.success("Feedback saved for this generation.")
                else:
                    with st.form(f"feedback_form_{run_id}", clear_on_submit=False):
                        fc1, fc2, fc3 = st.columns(3)
                        with fc1:
                            rating = st.slider("Overall rating", 1, 5, 4)
                        with fc2:
                            naturalness = st.slider("Naturalness", 1, 5, 4)
                        with fc3:
                            clarity = st.slider("Clarity", 1, 5, 4)

                        latency_acceptability = st.checkbox(
                            "Latency felt acceptable",
                            value=True,
                        )
                        comment = st.text_area(
                            "Comment",
                            height=80,
                            max_chars=2000,
                            placeholder="Optional notes about output quality, clarity, or workflow fit.",
                        )
                        feedback_submit = st.form_submit_button(
                            "Save Feedback",
                            use_container_width=True,
                        )

                    if feedback_submit:
                        feedback_resp = api_post_feedback(
                            run_id=run_id,
                            rating=rating,
                            naturalness=naturalness,
                            clarity=clarity,
                            latency_acceptability=latency_acceptability,
                            comment=comment,
                        )
                        if feedback_resp.get("success"):
                            st.session_state.feedback_submitted_for = run_id
                            st.success("Feedback saved.")
                        else:
                            st.error(
                                f"Could not save feedback: {feedback_resp.get('error', 'Unknown error')}"
                            )
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error(
                f"Generation failed: {result.get('error', 'Unknown error')}",
            )

        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — Dashboard
# ═══════════════════════════════════════════════════════════════════════════

with tab_dashboard:
    st.markdown(
        """
<div class="vp-section-header">
    <p class="vp-section-eyebrow">History</p>
    <h2 class="vp-section-title">Generation Runs</h2>
    <p class="vp-section-copy">Filter persisted synthesis runs by status, voice, language, and cache behavior.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="vp-filter-toolbar"><p class="vp-filter-toolbar-title">Filters</p>', unsafe_allow_html=True)
    # Filters
    f1, f2, f3, f4, f5 = st.columns([2, 2, 2, 2, 1])
    with f1:
        dash_status = st.selectbox("Status", ["all", "success", "failed"], key="dash_status")
    with f2:
        dash_voice = st.selectbox("Voice", ["all"] + voice_options, key="dash_voice")
    with f3:
        dash_lang = st.selectbox("Language", ["all"] + language_options, key="dash_lang")
    with f4:
        dash_cache = st.selectbox("Cache Hit", ["all", "true", "false"], key="dash_cache")
    with f5:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh = st.button("Refresh", key="dash_refresh", help="Refresh runs")

    st.markdown("</div>", unsafe_allow_html=True)

    # Build query params
    params: dict = {"limit": 50}
    if dash_status != "all":
        params["status"] = dash_status
    if dash_voice != "all":
        params["voice"] = dash_voice
    if dash_lang != "all":
        params["language"] = dash_lang
    if dash_cache != "all":
        params["cache_hit"] = dash_cache

    with st.spinner("Loading runs…"):
        runs_resp = api_get("/runs", params=params)

    if "_error" in runs_resp:
        st.warning(f"Could not fetch runs: {runs_resp['_error']}", icon="⚠️")
    else:
        runs = runs_resp if isinstance(runs_resp, list) else runs_resp.get("runs", runs_resp)
        if isinstance(runs, list) and len(runs) > 0:
            df = pd.DataFrame(runs)

            # Select & rename columns if they exist
            desired_cols = [
                "created_at", "text", "voice", "language", "engine",
                "latency_ms", "audio_duration_seconds", "cache_hit", "success",
            ]
            available_cols = [c for c in desired_cols if c in df.columns]
            if available_cols:
                df = df[available_cols]

            # Truncate text
            if "text" in df.columns:
                df["text"] = df["text"].astype(str).str[:80] + "…"

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "created_at": st.column_config.DatetimeColumn("Time", format="MMM DD, HH:mm:ss"),
                    "text": st.column_config.TextColumn("Text", width="large"),
                    "voice": st.column_config.TextColumn("Voice"),
                    "language": st.column_config.TextColumn("Lang"),
                    "engine": st.column_config.TextColumn("Engine"),
                    "latency_ms": st.column_config.NumberColumn("Latency (ms)", format="%.0f"),
                    "audio_duration_seconds": st.column_config.NumberColumn("Duration (s)", format="%.2f"),
                    "cache_hit": st.column_config.CheckboxColumn("Cache"),
                    "success": st.column_config.CheckboxColumn("Success"),
                },
            )
            st.caption(f"Showing {len(df)} run(s)")
        else:
            st.info("No runs found. Generate speech first.")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — Metrics
# ═══════════════════════════════════════════════════════════════════════════

with tab_metrics:
    st.markdown(
        """
<div class="vp-section-header">
    <p class="vp-section-eyebrow">Metrics</p>
    <h2 class="vp-section-title">System Performance</h2>
    <p class="vp-section-copy">Monitor process-local request counts, latency, cache behavior, engine usage, and evaluation feedback.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("Refresh Metrics", key="metrics_refresh"):
        st.cache_data.clear()

    with st.spinner("Loading metrics…"):
        metrics_resp = api_get("/metrics")

    if "_error" in metrics_resp:
        st.warning(f"Could not fetch metrics: {metrics_resp['_error']}", icon="⚠️")
    else:
        total = metrics_resp.get("total_requests", 0)
        success = metrics_resp.get("successful_requests", 0)
        failed = metrics_resp.get("failed_requests", 0)
        avg_lat = metrics_resp.get("average_latency_ms") or 0
        p95_lat = metrics_resp.get("p95_latency_ms")
        p95_display = f"{p95_lat:.0f}" if isinstance(p95_lat, (int, float)) else "—"
        cache_rate = metrics_resp.get("cache_hit_rate") or 0
        cache_count = metrics_resp.get("cache_hit_count", 0)
        top_voice = metrics_resp.get("most_used_voice") or "—"
        engine = metrics_resp.get("engine") or "—"
        feedback_count = metrics_resp.get("feedback_count", 0)
        avg_rating = metrics_resp.get("average_rating")
        avg_naturalness = metrics_resp.get("average_naturalness")
        avg_clarity = metrics_resp.get("average_clarity")

        success_rate = (success / total * 100) if total > 0 else 0

        st.markdown('<p class="vp-metrics-group-title">Request Overview</p>', unsafe_allow_html=True)
        # Row 1
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            st.markdown(
                f"""<div class="metric-card vp-metric-primary">
                    <div class="metric-label">Total Requests</div>
                    <div class="metric-value accent">{total:,}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with r1c2:
            st.markdown(
                f"""<div class="metric-card vp-metric-success">
                    <div class="metric-label">Success Rate</div>
                    <div class="metric-value secondary">{success_rate:.1f}<span style="font-size:0.85rem;font-weight:600;">%</span></div>
                </div>""",
                unsafe_allow_html=True,
            )
        with r1c3:
            failed_class = "danger" if failed > 0 else ""
            st.markdown(
                f"""<div class="metric-card {'vp-metric-danger' if failed > 0 else ''}">
                    <div class="metric-label">Failed Requests</div>
                    <div class="metric-value {failed_class}">{failed:,}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        st.markdown('<p class="vp-metrics-group-title">Latency & Cache</p>', unsafe_allow_html=True)
        # Row 2
        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            st.markdown(
                f"""<div class="metric-card vp-metric-primary">
                    <div class="metric-label">Avg Latency</div>
                    <div class="metric-value accent">{avg_lat:.0f}<span style="font-size:0.85rem;font-weight:600;"> ms</span></div>
                </div>""",
                unsafe_allow_html=True,
            )
        with r2c2:
            st.markdown(
                f"""<div class="metric-card vp-metric-warning">
                    <div class="metric-label">P95 Latency</div>
                    <div class="metric-value warning">{p95_display}<span style="font-size:0.85rem;font-weight:600;"> ms</span></div>
                </div>""",
                unsafe_allow_html=True,
            )
        with r2c3:
            cache_pct = cache_rate * 100 if cache_rate <= 1 else cache_rate
            st.markdown(
                f"""<div class="metric-card vp-metric-accent">
                    <div class="metric-label">Cache Hit Rate</div>
                    <div class="metric-value secondary">{cache_pct:.1f}<span style="font-size:0.85rem;font-weight:600;">%</span></div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        st.markdown('<p class="vp-metrics-group-title">Engine Highlights</p>', unsafe_allow_html=True)
        # Row 3 — highlights
        r3c1, r3c2 = st.columns(2)
        with r3c1:
            st.markdown(
                f"""<div class="metric-card vp-card-accent">
                    <div class="metric-label">Most Used Voice</div>
                    <div class="metric-value" style="font-size:1.2rem;">{top_voice}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with r3c2:
            st.markdown(
                f"""<div class="metric-card vp-card-secondary">
                    <div class="metric-label">Active Engine</div>
                    <div class="metric-value" style="font-size:1.2rem;">{engine}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        st.markdown('<p class="vp-metrics-group-title">Evaluation Feedback</p>', unsafe_allow_html=True)
        # Row 4 — feedback loop
        r4c1, r4c2, r4c3, r4c4 = st.columns(4)
        rating_display = f"{avg_rating:.2f}" if isinstance(avg_rating, (int, float)) else "—"
        naturalness_display = (
            f"{avg_naturalness:.2f}" if isinstance(avg_naturalness, (int, float)) else "—"
        )
        clarity_display = f"{avg_clarity:.2f}" if isinstance(avg_clarity, (int, float)) else "—"
        with r4c1:
            st.markdown(
                f"""<div class="metric-card vp-metric-primary">
                    <div class="metric-label">Feedback Count</div>
                    <div class="metric-value accent">{feedback_count:,}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with r4c2:
            st.markdown(
                f"""<div class="metric-card vp-metric-accent">
                    <div class="metric-label">Avg Rating</div>
                    <div class="metric-value secondary">{rating_display}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with r4c3:
            st.markdown(
                f"""<div class="metric-card">
                    <div class="metric-label">Avg Naturalness</div>
                    <div class="metric-value">{naturalness_display}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with r4c4:
            st.markdown(
                f"""<div class="metric-card">
                    <div class="metric-label">Avg Clarity</div>
                    <div class="metric-value">{clarity_display}</div>
                </div>""",
                unsafe_allow_html=True,
            )


# Close app shell
st.markdown("</div></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    """
<div class="vp-footer">
    <p>Built for TTS product infrastructure, evaluation, and observability</p>
    <p><span class="vp-footer-brand">VoxPilot</span> v1.0.0 · Powered by Streamlit & FastAPI</p>
</div>
""",
    unsafe_allow_html=True,
)
