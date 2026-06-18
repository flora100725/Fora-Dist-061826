# app.py
# M-ARCH-0616 TFDA Compliance Hub (Streamlit Space Edition)
# Version: v2.5.0-WOW-AI-ExpansionPack (EGEL + CGFS + ROPG)
#
# Notes:
# - This Streamlit app is designed to run on Hugging Face Spaces.
# - It preserves the platform’s core features (dataset ingest, anomaly detection, GIS view,
#   agentic war room, grounded chat-like execution) and adds three “WOW AI” modules:
#   6.4 Evidence Graph & Explainability Ledger (EGEL)
#   6.5 Counterfeit & Grey-Market Forensics Studio (CGFS)
#   6.6 Recall Orchestrator & Playbook Generator (ROPG)
#
# - Multi-provider LLM support: Gemini / OpenAI / Anthropic / XAI (best-effort).
# - API key handling:
#   - If key exists in environment, UI will NOT show the key or prompt for it.
#   - If missing, user can input via password field (stored only in session_state).
#
# - No secrets are printed. No keys are logged.
# - Optional dependencies are handled gracefully (features degrade rather than crash).

from __future__ import annotations

import io
import os
import re
import json
import time
import math
import uuid
import base64
import hashlib
import textwrap
import datetime as dt
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Iterable

import streamlit as st

# Core deps (expected)
try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

# Optional deps
try:
    import pydeck as pdk
except Exception:  # pragma: no cover
    pdk = None

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

try:
    import networkx as nx
except Exception:  # pragma: no cover
    nx = None

# ----------------------------
# App constants & i18n
# ----------------------------

APP_TITLE = "M-ARCH-0616 TFDA Compliance Hub — WOW AI Expansion Pack"
APP_VERSION = "v2.5.0-WOW-AI-ExpansionPack"

DEFAULT_MAX_TOKENS = 12000
DEFAULT_MODEL = "gemini-3.1-flash-lite"

PROVIDERS = ["Gemini", "OpenAI", "Anthropic", "XAI"]
ENV_KEY_NAMES = {
    "Gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    "OpenAI": ["OPENAI_API_KEY"],
    "Anthropic": ["ANTHROPIC_API_KEY"],
    "XAI": ["XAI_API_KEY", "GROK_API_KEY"],
}

MODEL_CATALOG = {
    "Gemini": [
        "gemini-3.1-flash-lite",
        "gemini-3-flash-preview",
        "gemini-3.5-flash",
        "gemini-3.1-pro-preview",
    ],
    "OpenAI": [
        "gpt-4o-mini",
        "gpt-5-mini",
        "gpt-5-nano",
    ],
    "Anthropic": [
        "claude-3-5-sonnet-latest",
        "claude-3-5-haiku-latest",
        "claude-3-opus-latest",
    ],
    "XAI": [
        "grok-2-mini",
        "grok-2",
    ],
}

LANGS = ["English", "繁體中文（預設）"]
DEFAULT_LANG = "繁體中文（預設）"

I18N = {
    "app_subtitle": {
        "English": "Regulatory analytics + evidence-grade AI for medical device logistics.",
        "繁體中文（預設）": "醫療器材流向合規分析 + 證據級 AI 強化（稽核/召回/取締）。",
    },
    "sidebar_ui": {
        "English": "UI Settings",
        "繁體中文（預設）": "介面設定",
    },
    "sidebar_security": {
        "English": "API / Security",
        "繁體中文（預設）": "API / 安全",
    },
    "sidebar_data": {
        "English": "Data",
        "繁體中文（預設）": "資料",
    },
    "provider_configured": {
        "English": "Configured from environment",
        "繁體中文（預設）": "已由環境變數配置",
    },
    "provider_missing": {
        "English": "No key detected (fallback rules engine available)",
        "繁體中文（預設）": "未偵測到金鑰（可使用規則引擎備援）",
    },
    "tabs": {
        "English": [
            "Dashboard",
            "GIS Map",
            "Ledger & Anomalies",
            "Agentic Workbench",
            "AI Note Keeper",
            "Forensics Studio (CGFS)",
            "Evidence Graph (EGEL)",
            "Recall Console (ROPG)",
            "Config: agents.yaml / SKILL.md",
        ],
        "繁體中文（預設）": [
            "總覽儀表板",
            "GIS 地圖",
            "帳冊與異常",
            "代理人工作台",
            "AI 記事本",
            "鑑識工作室（CGFS）",
            "證據圖譜（EGEL）",
            "召回控制台（ROPG）",
            "設定：agents.yaml / SKILL.md",
        ],
    },
}

# 10 Pantone-inspired palettes (approximate; brand-safe)
PANTONE_STYLES = [
    {"name": "Classic Blue", "primary": "#0F4C81", "accent": "#5DADEC", "bg": "#F6F9FC", "fg": "#0B1220"},
    {"name": "Living Coral", "primary": "#FF6F61", "accent": "#FFA69E", "bg": "#FFF7F6", "fg": "#231815"},
    {"name": "Ultra Violet", "primary": "#5F4B8B", "accent": "#B39DDB", "bg": "#F7F4FB", "fg": "#140F1F"},
    {"name": "Emerald", "primary": "#009B77", "accent": "#7FD1AE", "bg": "#F3FBF8", "fg": "#0A1A14"},
    {"name": "Tangerine Tango", "primary": "#DD4124", "accent": "#FF9A76", "bg": "#FFF6F2", "fg": "#1F0E08"},
    {"name": "Illuminating", "primary": "#F5DF4D", "accent": "#FFF1A6", "bg": "#FFFDF0", "fg": "#1A1A12"},
    {"name": "Very Peri", "primary": "#6667AB", "accent": "#A9A9D9", "bg": "#F5F5FF", "fg": "#121225"},
    {"name": "Rose Quartz", "primary": "#F7CAC9", "accent": "#FADDE1", "bg": "#FFF7FA", "fg": "#23161A"},
    {"name": "Greenery", "primary": "#88B04B", "accent": "#CDE7A8", "bg": "#F7FBF2", "fg": "#141C0A"},
    {"name": "Black Onyx", "primary": "#1B1B1D", "accent": "#6B7280", "bg": "#0B0C0F", "fg": "#F4F5F7"},
]

THEMES = ["Sleek Light", "Sleek Dark"]


def t(key: str) -> str:
    lang = st.session_state.get("lang", DEFAULT_LANG)
    return I18N.get(key, {}).get(lang, I18N.get(key, {}).get(DEFAULT_LANG, key))


# ----------------------------
# Utility: safety, hashing, parsing
# ----------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def parse_yyyymmdd(s: str) -> Optional[dt.date]:
    if not s:
        return None
    s = str(s).strip()
    m = re.fullmatch(r"(\d{4})[/-]?(\d{2})[/-]?(\d{2})", s)
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except Exception:
        return None


SERIAL_CLEAN_RE = re.compile(r"[^A-Z0-9]+")


def normalize_serial(raw: str) -> str:
    """
    Normalizes serial numbers by:
    - uppercasing
    - removing whitespace and separators
    - stripping trailing local suffix stamps (heuristic)
    Examples:
    - RNJ146480G2001 -> RNJ146480G
    - RNJ146480G/A-01 -> RNJ146480G
    """
    if raw is None:
        return ""
    s = str(raw).upper().strip()

    # Remove common hospital/local suffix patterns: slash segments, dash segments, Chinese prefixes
    s = re.sub(r"^[\u4e00-\u9fffA-Z]{1,6}[-_：:]\s*", "", s)  # leading org stamp like "臺大-"
    s = s.split("/")[0]  # keep base before slash
    s = s.split(" ")[0]  # keep first token

    # Remove non-alnum
    s2 = SERIAL_CLEAN_RE.sub("", s)

    # Heuristic: if ends with 3-6 digits and prefix looks like canonical serial, drop digits
    m = re.fullmatch(r"([A-Z]{2,4}\d{3,8}[A-Z])(\d{3,6})", s2)
    if m:
        return m.group(1)
    return s2


def clamp_int(x: Any, lo: int, hi: int, default: int) -> int:
    try:
        v = int(x)
        return max(lo, min(hi, v))
    except Exception:
        return default


def md_escape(s: str) -> str:
    # Minimal markdown escaping for table cells
    return str(s).replace("|", "\\|")


# ----------------------------
# Session initialization
# ----------------------------

def init_session() -> None:
    ss = st.session_state

    ss.setdefault("lang", DEFAULT_LANG)
    ss.setdefault("theme", "Sleek Light")
    ss.setdefault("style_idx", 0)
    ss.setdefault("provider", "Gemini")
    ss.setdefault("model", DEFAULT_MODEL)
    ss.setdefault("max_tokens", DEFAULT_MAX_TOKENS)
    ss.setdefault("temperature", 0.2)

    ss.setdefault("logs", [])  # list[str]
    ss.setdefault("ai_traces", [])  # list[dict]
    ss.setdefault("artifacts", {})  # id -> dict metadata + bytes (ephemeral)
    ss.setdefault("evidence_links", [])  # list of links
    ss.setdefault("graph_snapshot", None)

    ss.setdefault("agents_yaml_text", default_agents_yaml())
    ss.setdefault("skill_md_text", default_skill_md())

    ss.setdefault("agents", [])  # parsed agents list
    ss.setdefault("agent_outputs", [])  # list of dict: agent_name, output, edited_output, ts

    ss.setdefault("note_raw", "")
    ss.setdefault("note_md", "")

    ss.setdefault("distributions_df", None)
    ss.setdefault("purchases_df", None)
    ss.setdefault("anomalies", [])
    ss.setdefault("compliance_score", 100)

    ss.setdefault("permit_expiry_map", {
        "029878": "2026-02-28",
        "030747": "2028-12-31",
    })

    ss.setdefault("recall_plans", [])  # list of dict


def default_agents_yaml() -> str:
    return textwrap.dedent(
        """\
        # agents.yaml (default)
        # Minimal, standardized schema:
        # - name: string (required)
        # - role: string (optional)
        # - system: string (required)
        # - goal: string (optional)
        # - output_format: "markdown" | "text" | "json" (optional)
        # - guardrails: list[string] (optional)
        agents:
          - name: "Logistics Master"
            role: "Supply-chain optimizer"
            system: |
              You are a logistics optimization expert for Taiwan medical device distribution.
              Focus on stock balancing, hub transfer plans, and operational feasibility.
            goal: "Propose a safe and efficient redistribution plan and highlight bottlenecks."
            output_format: "markdown"
            guardrails:
              - "Cite anomalies by ID when referenced."
              - "Avoid definitive clinical claims; recommend verification steps."

          - name: "Compliance Overlord"
            role: "TFDA compliance auditor"
            system: |
              You are a senior TFDA medical device auditor specialized in TUDID/UDI and import permits.
              Focus on violations: expired permits, duplicates, timeline inversions, unit mismatch.
            goal: "Produce enforcement-grade findings, legal basis, and required next evidence."
            output_format: "markdown"
            guardrails:
              - "Use professional Traditional Chinese if UI language is Chinese."
              - "Provide actionable items and cite evidence IDs."

          - name: "Biomedical Engineer"
            role: "Biomedical risk analyst"
            system: |
              You are a biomedical engineer focusing on pacemaker safety signals and device integrity.
              Do not speculate; infer only from provided data and evidence.
            goal: "Assess risk signals and recommend quarantine/inspection/recall thresholds."
            output_format: "markdown"
            guardrails:
              - "No patient-specific advice; keep at device logistics and safety process level."
        """
    ).strip() + "\n"


def default_skill_md() -> str:
    return textwrap.dedent(
        """\
        # SKILL.md (default)

        ## Core Skills
        - TFDA medical device logistics compliance auditing
        - TUDID / UDI reasoning, serial normalization, duplicate detection
        - Timeline inversion investigation (delivery vs receive dates)
        - Permit expiry verification (Article 25 awareness)
        - Evidence-grade writing (citations, assumptions, next-evidence checklist)
        - Recall simulation and action planning
        - Counterfeit / grey-market suspicion signal reporting (non-definitive)

        ## Style
        - Default language: Traditional Chinese
        - Output: structured markdown with headings, tables, and numbered actions
        - Always cite internal IDs: anomaly_id, artifact_id, device_serial_norm
        """
    ).strip() + "\n"


# ----------------------------
# WOW UI: Theme + palette CSS
# ----------------------------

def inject_css(theme: str, palette: Dict[str, str]) -> None:
    is_dark = theme.lower().endswith("dark")
    bg = palette["bg"]
    fg = palette["fg"]
    primary = palette["primary"]
    accent = palette["accent"]

    # Streamlit theming via CSS injection (best-effort; Streamlit DOM can change)
    css = f"""
    <style>
      :root {{
        --wow-bg: {bg};
        --wow-fg: {fg};
        --wow-primary: {primary};
        --wow-accent: {accent};
      }}

      .stApp {{
        background: var(--wow-bg);
        color: var(--wow-fg);
      }}

      /* Headings */
      h1, h2, h3, h4 {{
        color: var(--wow-fg);
      }}

      /* Buttons */
      div.stButton > button {{
        border-radius: 12px;
        border: 1px solid rgba(127,127,127,0.25);
        background: linear-gradient(135deg, var(--wow-primary), var(--wow-accent));
        color: #fff;
        font-weight: 600;
      }}
      div.stButton > button:hover {{
        filter: brightness(1.03);
        transform: translateY(-1px);
      }}

      /* Badges */
      .wow-badge {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        border: 1px solid rgba(127,127,127,0.25);
        background: rgba(127,127,127,0.10);
      }}

      /* Panels */
      .wow-panel {{
        border: 1px solid rgba(127,127,127,0.20);
        border-radius: 16px;
        padding: 14px 14px;
        background: {"rgba(255,255,255,0.60)" if not is_dark else "rgba(20,20,25,0.55)"};
        backdrop-filter: blur(10px);
      }}

      /* Coral keyword highlight */
      .kw-coral {{
        color: coral;
        font-weight: 700;
      }}

      /* Code blocks contrast */
      pre {{
        border-radius: 12px;
      }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ----------------------------
# Artifact & trace logging
# ----------------------------

def log(msg: str) -> None:
    st.session_state.logs.append(f"[{safe_now_iso()}] {msg}")


def add_ai_trace(trace: Dict[str, Any]) -> None:
    # Never store raw API keys; never include them in trace.
    trace = dict(trace)
    trace.setdefault("trace_id", str(uuid.uuid4()))
    trace.setdefault("ts", safe_now_iso())
    st.session_state.ai_traces.append(trace)


def upsert_artifact(name: str, mime: str, data: bytes, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    artifact_id = str(uuid.uuid4())
    meta = {
        "artifact_id": artifact_id,
        "name": name,
        "mime": mime,
        "size": len(data),
        "sha256": sha256_bytes(data),
        "uploaded_at": safe_now_iso(),
        "tags": tags or [],
        "status": "UPLOADED",
        "notes": "",
    }
    st.session_state.artifacts[artifact_id] = {"meta": meta, "data": data}
    log(f"Artifact uploaded: {name} ({mime}, {len(data)} bytes) id={artifact_id}")
    return meta


def download_button(label: str, data: bytes, file_name: str, mime: str) -> None:
    st.download_button(label, data=data, file_name=file_name, mime=mime)


# ----------------------------
# YAML standardization (agents.yaml)
# ----------------------------

REQUIRED_AGENT_FIELDS = ["name", "system"]


def standardize_agents_yaml(yaml_text: str) -> Tuple[Optional[List[Dict[str, Any]]], List[str], str]:
    """
    Returns: (agents_list_or_none, errors, standardized_yaml_text)
    Standardization:
      - Must have top-level key 'agents' as list
      - Each agent must have name/system; set defaults for missing optional fields
      - Normalize output_format to one of markdown/text/json
      - guardrails must be list[str]
    """
    errors: List[str] = []
    if yaml is None:
        return None, ["pyyaml is not installed; cannot parse agents.yaml"], yaml_text

    try:
        obj = yaml.safe_load(yaml_text) or {}
    except Exception as e:
        return None, [f"YAML parse error: {e}"], yaml_text

    if not isinstance(obj, dict):
        return None, ["Top-level YAML must be a mapping/dict."], yaml_text

    agents = obj.get("agents")
    if not isinstance(agents, list):
        return None, ["Missing or invalid 'agents' list."], yaml_text

    standardized: List[Dict[str, Any]] = []
    for i, a in enumerate(agents):
        if not isinstance(a, dict):
            errors.append(f"Agent #{i+1} must be a mapping/dict.")
            continue

        for f in REQUIRED_AGENT_FIELDS:
            if not str(a.get(f, "")).strip():
                errors.append(f"Agent #{i+1} missing required field: {f}")

        output_format = str(a.get("output_format", "markdown")).strip().lower()
        if output_format not in ("markdown", "text", "json"):
            output_format = "markdown"

        guardrails = a.get("guardrails", [])
        if guardrails is None:
            guardrails = []
        if isinstance(guardrails, str):
            guardrails = [guardrails]
        if not isinstance(guardrails, list) or not all(isinstance(x, str) for x in guardrails):
            guardrails = []
            errors.append(f"Agent #{i+1} guardrails must be list[str]. Reset to [].")

        standardized.append({
            "name": str(a.get("name", "")).strip(),
            "role": str(a.get("role", "")).strip(),
            "system": str(a.get("system", "")).rstrip(),
            "goal": str(a.get("goal", "")).strip(),
            "output_format": output_format,
            "guardrails": guardrails,
        })

    std_obj = {"agents": standardized}
    std_yaml = yaml.safe_dump(std_obj, sort_keys=False, allow_unicode=True)

    return (standardized if not errors else standardized), errors, std_yaml


# ----------------------------
# Data: sample dataset + anomalies
# ----------------------------

def sample_distributions_df() -> "pd.DataFrame":
    rows = [
        {
            "no": 521, "reporter": "B00047", "deliveryDate": "20260331", "target": "台大醫院",
            "permitNo": "030747", "category": "Pacemaker", "udid": "TUDID-XXX-030747",
            "chineseName": "心臟節律器", "batchNo": "", "serialNo": "RNE644378S", "modelNo": "W2SR01",
            "quantity": 1, "unit": "個", "mfgDate": "20250115", "expDate": "20300115", "shelfLife": "60M"
        },
        {
            "no": 522, "reporter": "B00446", "deliveryDate": "20260412", "target": "奇美永康",
            "permitNo": "029878", "category": "Pacemaker", "udid": "TUDID-XXX-029878",
            "chineseName": "心臟節律器", "batchNo": "", "serialNo": "RNE644378S", "modelNo": "W3DR01",
            "quantity": 1, "unit": "個", "mfgDate": "20250115", "expDate": "20300115", "shelfLife": "60M"
        },
        {
            "no": 523, "reporter": "B00047", "deliveryDate": "20260331", "target": "林口長庚",
            "permitNo": "030747", "category": "Pacemaker", "udid": "TUDID-XXX-030747",
            "chineseName": "心臟節律器", "batchNo": "", "serialNo": "RNJ146480G", "modelNo": "W2SR01",
            "quantity": 1, "unit": "個", "mfgDate": "20241010", "expDate": "20291010", "shelfLife": "60M"
        },
    ]
    return pd.DataFrame(rows)


def sample_purchases_df() -> "pd.DataFrame":
    rows = [
        {
            "no": 150, "reporter": "C00306", "receiveDate": "20260310", "supplier": "林口長庚",
            "permitNo": "030747", "chineseName": "心臟節律器", "udiDi": "UDI-DI-030747",
            "category": "Pacemaker", "batchNo": "", "serialNo": "RNJ146480G2001", "modelNo": "W2SR01",
            "quantity": 1, "unit": "個", "mfgDate": "20241010", "expDate": "20291010", "shelfLife": "60M",
            "returnInfo": 0, "remainingQty": 1, "createdDate": "20260310"
        }
    ]
    return pd.DataFrame(rows)


def ensure_dataframes() -> None:
    if pd is None:
        st.error("pandas is required but not installed.")
        st.stop()

    if st.session_state.distributions_df is None:
        st.session_state.distributions_df = sample_distributions_df()
    if st.session_state.purchases_df is None:
        st.session_state.purchases_df = sample_purchases_df()


def compute_compliance_score(anomalies: List[Dict[str, Any]]) -> int:
    base = 100
    penalty_map = {"CRITICAL": 20, "HIGH": 12, "WARNING": 5}
    total_penalty = 0
    for a in anomalies:
        if a.get("resolved"):
            continue
        total_penalty += penalty_map.get(a.get("severity", "WARNING"), 5)
    return max(0, base - total_penalty)


def detect_anomalies(distributions: "pd.DataFrame", purchases: "pd.DataFrame", permit_expiry_map: Dict[str, str]) -> List[Dict[str, Any]]:
    anomalies: List[Dict[str, Any]] = []

    # Build normalized serial indices
    dist = distributions.copy()
    pur = purchases.copy()
    dist["serial_norm"] = dist["serialNo"].apply(normalize_serial)
    pur["serial_norm"] = pur["serialNo"].apply(normalize_serial)

    # 1) Duplicate serial in distributions
    dup = dist.groupby("serial_norm").size().reset_index(name="cnt")
    dup = dup[(dup["serial_norm"] != "") & (dup["cnt"] > 1)]
    for _, r in dup.iterrows():
        sn = r["serial_norm"]
        rows = dist[dist["serial_norm"] == sn]
        targets = ", ".join(rows["target"].astype(str).tolist()[:4])
        anomalies.append({
            "id": f"ANOM-{uuid.uuid4().hex[:8].upper()}",
            "type": "DUPLICATE_SERIAL",
            "severity": "CRITICAL",
            "title": f"Duplicate serial detected: {sn}",
            "description": f"Serial {sn} appears in multiple distribution records. Targets: {targets}",
            "itemRef": sn,
            "date": safe_now_iso(),
            "source": "auto-detector",
            "resolved": False,
            "evidence": {"serial_norm": sn, "targets": targets},
        })

    # 2) Timeline inversion: purchase receive < distribution delivery (matching serial)
    dist_min = dist.groupby("serial_norm")["deliveryDate"].min().to_dict()
    for _, row in pur.iterrows():
        sn = row["serial_norm"]
        if not sn or sn not in dist_min:
            continue
        rec = parse_yyyymmdd(row.get("receiveDate", ""))
        deliv = parse_yyyymmdd(dist_min[sn])
        if rec and deliv and rec < deliv:
            anomalies.append({
                "id": f"ANOM-{uuid.uuid4().hex[:8].upper()}",
                "type": "TIMELINE_INVERSION",
                "severity": "HIGH",
                "title": f"Timeline inversion: {sn}",
                "description": f"Receive date {rec} is earlier than delivery date {deliv}.",
                "itemRef": sn,
                "date": safe_now_iso(),
                "source": "auto-detector",
                "resolved": False,
                "evidence": {"serial_norm": sn, "receiveDate": str(rec), "deliveryDate": str(deliv)},
            })

    # 3) Expired permit: deliveryDate after expiry
    for _, row in dist.iterrows():
        permit = str(row.get("permitNo", "")).strip()
        expiry = permit_expiry_map.get(permit)
        if not expiry:
            continue
        exp = parse_yyyymmdd(expiry)
        deliv = parse_yyyymmdd(row.get("deliveryDate", ""))
        if exp and deliv and deliv > exp:
            anomalies.append({
                "id": f"ANOM-{uuid.uuid4().hex[:8].upper()}",
                "type": "EXPIRED_PERMIT",
                "severity": "CRITICAL",
                "title": f"Expired permit usage: {permit}",
                "description": f"Delivery date {deliv} occurs after permit expiry {exp}.",
                "itemRef": permit,
                "date": safe_now_iso(),
                "source": "auto-detector",
                "resolved": False,
                "evidence": {"permitNo": permit, "deliveryDate": str(deliv), "expiry": str(exp)},
            })

    return anomalies


# ----------------------------
# LLM provider wrappers (best-effort)
# ----------------------------

def env_key_for(provider: str) -> Optional[str]:
    for k in ENV_KEY_NAMES.get(provider, []):
        v = os.environ.get(k)
        if v:
            return v
    return None


def get_runtime_key(provider: str) -> Optional[str]:
    # If environment key exists, prefer it (and do not show it).
    k = env_key_for(provider)
    if k:
        return k
    # else allow user-provided key stored in session
    return st.session_state.get("api_keys", {}).get(provider)


def llm_available(provider: str) -> bool:
    return bool(get_runtime_key(provider))


def build_system_prompt(base_system: str, skill_md: str, lang: str, guardrails: List[str]) -> str:
    lang_hint = "Answer in Traditional Chinese." if "繁體中文" in lang else "Answer in English."
    gr = "\n".join([f"- {g}" for g in guardrails]) if guardrails else "- (none)"
    return f"""{base_system}

[LANGUAGE]
{lang_hint}

[SKILL]
{skill_md}

[GUARDRAILS]
{gr}
""".strip()


def fallback_llm_response(task_name: str, user_prompt: str, context: Dict[str, Any], lang: str) -> str:
    # Deterministic fallback: provides structured output without calling external APIs.
    if "繁體中文" in lang:
        return f"""#（備援輸出）{task_name}

## 使用者需求
{user_prompt}

## 系統判讀（規則引擎/靜態模板）
- 目前未配置 API 金鑰，已使用可重現的備援模板輸出。
- 請先於側邊欄設定 Gemini/OpenAI/Anthropic/XAI 金鑰以啟用 LLM 推理與寫作。

## 建議下一步
1. 檢視異常清單（duplicate serial / timeline inversion / expired permit）。
2. 將相關交易列與證據文件上傳至「鑑識工作室（CGFS）」。
3. 於「召回控制台（ROPG）」建立模擬方案並輸出 playbook。

## 引用
- context keys: {", ".join(sorted(context.keys()))}
"""
    return f"""# (Fallback Output) {task_name}

## User request
{user_prompt}

## Deterministic notes
- No API key configured; generated using a reproducible fallback template.
- Configure a provider key in the sidebar to enable live LLM reasoning.

## Next steps
1. Review anomalies list.
2. Upload evidence in Forensics Studio (CGFS).
3. Create a recall simulation in Recall Console (ROPG).

## Context keys
{", ".join(sorted(context.keys()))}
"""


def call_llm(provider: str, model: str, system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> str:
    """
    Best-effort multi-provider LLM call.
    If any error occurs or key missing, returns deterministic fallback.
    """
    lang = st.session_state.get("lang", DEFAULT_LANG)
    ctx = {"provider": provider, "model": model, "max_tokens": max_tokens}

    key = get_runtime_key(provider)
    if not key:
        add_ai_trace({
            "provider": provider,
            "model": model,
            "status": "FALLBACK_NO_KEY",
            "prompt_fingerprint": sha256_bytes((system_prompt + "\n" + user_prompt).encode("utf-8")),
        })
        return fallback_llm_response(task_name=f"{provider}:{model}", user_prompt=user_prompt, context=ctx, lang=lang)

    started = time.time()
    prompt_fp = sha256_bytes((system_prompt + "\n" + user_prompt).encode("utf-8"))

    try:
        text = None

        if provider == "Gemini":
            # Preferred: google-genai (new). Fallback: google.generativeai (legacy).
            try:
                from google import genai  # type: ignore
                client = genai.Client(api_key=key)
                # Simple generate call (non-streaming)
                resp = client.models.generate_content(
                    model=model,
                    contents=user_prompt,
                    config={
                        "system_instruction": system_prompt,
                        "temperature": float(temperature),
                        "max_output_tokens": int(max_tokens),
                    },
                )
                text = getattr(resp, "text", None) or str(resp)
            except Exception:
                try:
                    import google.generativeai as genai_legacy  # type: ignore
                    genai_legacy.configure(api_key=key)
                    m = genai_legacy.GenerativeModel(model_name=model, system_instruction=system_prompt)
                    resp = m.generate_content(user_prompt, generation_config={
                        "temperature": float(temperature),
                        "max_output_tokens": int(max_tokens),
                    })
                    text = getattr(resp, "text", None) or str(resp)
                except Exception as e:
                    raise RuntimeError(f"Gemini client error: {e}")

        elif provider == "OpenAI":
            try:
                from openai import OpenAI  # type: ignore
                client = OpenAI(api_key=key)
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=float(temperature),
                    max_tokens=int(max_tokens),
                )
                text = resp.choices[0].message.content or ""
            except Exception as e:
                raise RuntimeError(f"OpenAI client error: {e}")

        elif provider == "Anthropic":
            try:
                import anthropic  # type: ignore
                client = anthropic.Anthropic(api_key=key)
                resp = client.messages.create(
                    model=model,
                    max_tokens=int(max_tokens),
                    temperature=float(temperature),
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                # resp.content is list[TextBlock]
                parts = []
                for c in getattr(resp, "content", []):
                    parts.append(getattr(c, "text", str(c)))
                text = "".join(parts).strip()
            except Exception as e:
                raise RuntimeError(f"Anthropic client error: {e}")

        elif provider == "XAI":
            # XAI can be OpenAI-compatible; we attempt via openai client with base_url if provided.
            # If not available, fallback to deterministic response.
            base_url = os.environ.get("XAI_BASE_URL", "").strip() or "https://api.x.ai/v1"
            try:
                from openai import OpenAI  # type: ignore
                client = OpenAI(api_key=key, base_url=base_url)
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=float(temperature),
                    max_tokens=int(max_tokens),
                )
                text = resp.choices[0].message.content or ""
            except Exception as e:
                raise RuntimeError(f"XAI(OpenAI-compatible) client error: {e}")

        else:
            raise RuntimeError(f"Unsupported provider: {provider}")

        elapsed = time.time() - started
        add_ai_trace({
            "provider": provider,
            "model": model,
            "status": "OK",
            "latency_s": round(elapsed, 3),
            "prompt_fingerprint": prompt_fp,
            "output_fingerprint": sha256_bytes((text or "").encode("utf-8")),
        })
        return text or ""

    except Exception as e:
        elapsed = time.time() - started
        add_ai_trace({
            "provider": provider,
            "model": model,
            "status": "FALLBACK_ERROR",
            "latency_s": round(elapsed, 3),
            "prompt_fingerprint": prompt_fp,
            "error": str(e),
        })
        return fallback_llm_response(task_name=f"{provider}:{model} (error fallback)", user_prompt=user_prompt, context=ctx, lang=lang)


# ----------------------------
# Note processing & "AI Magics"
# ----------------------------

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    if PdfReader is None:
        return "(PDF extraction unavailable: pypdf not installed)"
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        parts = []
        for page in reader.pages[:50]:  # safety cap
            parts.append(page.extract_text() or "")
        return "\n".join(parts).strip()
    except Exception as e:
        return f"(PDF extraction error: {e})"


def simple_keyword_extract(text: str, top_k: int = 12) -> List[str]:
    # Deterministic heuristic: CJK+ASCII tokens, frequency-based with stoplist
    if not text:
        return []
    stop = set(["the", "and", "or", "to", "of", "in", "for", "with", "a", "an", "is", "are"])
    # Tokenize: words + CJK runs
    tokens = re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z]{3,}|\d{3,}", text)
    freq: Dict[str, int] = {}
    for tok in tokens:
        tok_l = tok.lower()
        if tok_l in stop:
            continue
        if len(tok) > 32:
            continue
        freq[tok] = freq.get(tok, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:top_k]
    return [k for k, _ in ranked]


def highlight_keywords_markdown(md: str, keywords: List[str], color: str = "coral") -> str:
    # Use HTML spans; Streamlit must render with unsafe_allow_html=True when displayed.
    if not md or not keywords:
        return md
    # Avoid breaking code blocks: we do a lightweight split and skip fenced blocks.
    parts = re.split(r"(```[\s\S]*?```)", md)
    out = []
    for p in parts:
        if p.startswith("```") and p.endswith("```"):
            out.append(p)
            continue
        q = p
        for kw in sorted(set(keywords), key=len, reverse=True):
            if not kw.strip():
                continue
            # Word boundary for ascii; direct for CJK
            if re.fullmatch(r"[A-Za-z0-9_ -]+", kw):
                q = re.sub(rf"\b({re.escape(kw)})\b", rf"<span class='kw-coral' style='color:{color};'>\1</span>", q)
            else:
                q = q.replace(kw, f"<span class='kw-coral' style='color:{color};'>{kw}</span>")
        out.append(q)
    return "".join(out)


def ai_magic_transform(note_text: str, mode: str, provider: str, model: str, max_tokens: int, temperature: float, lang: str) -> str:
    if mode == "Organize Markdown":
        sys = "You transform messy notes into a well-structured Markdown document with clear headings, bullet points, and action items."
        user = f"Transform the following note into organized Markdown:\n\n---\n{note_text}\n---"
    elif mode == "Summarize":
        sys = "You create a concise but information-dense summary with key risks and next steps."
        user = f"Summarize the following text:\n\n---\n{note_text}\n---"
    elif mode == "Action Items":
        sys = "You extract actionable tasks with owners (if mentioned), deadlines (if present), and verification criteria."
        user = f"Extract action items from:\n\n---\n{note_text}\n---"
    elif mode == "Flashcards Q&A":
        sys = "You produce study flashcards (Q/A) from the note."
        user = f"Create 10 flashcards from:\n\n---\n{note_text}\n---"
    elif mode == "Compliance Tone Rewrite":
        sys = "You rewrite content into a formal TFDA audit tone, with neutral wording and evidence-oriented phrasing."
        user = f"Rewrite in compliance/audit tone:\n\n---\n{note_text}\n---"
    elif mode == "Translate (EN<->ZH-TW)":
        sys = "Translate faithfully, preserving technical terms, serial numbers, and permit numbers."
        user = f"Translate (auto-detect direction) the following:\n\n---\n{note_text}\n---"
    elif mode == "WOW: Evidence Memo (EGEL)":
        sys = "You generate an evidence-grade memo with explicit citations placeholders (artifact_id/anomaly_id/serial_norm)."
        user = f"Draft an evidence memo from the following content:\n\n---\n{note_text}\n---"
    elif mode == "WOW: Counterfeit Suspicion Signals (CGFS)":
        sys = "You list counterfeit/grey-market suspicion signals without making definitive claims; recommend verification steps."
        user = f"Analyze for suspicion signals:\n\n---\n{note_text}\n---"
    elif mode == "WOW: Recall Playbook (ROPG)":
        sys = "You create a recall playbook outline with phases, tasks, communications, and closure criteria."
        user = f"Create a recall playbook:\n\n---\n{note_text}\n---"
    else:
        sys = "You are a helpful assistant."
        user = note_text

    system_prompt = sys + ("\nAnswer in Traditional Chinese." if "繁體中文" in lang else "\nAnswer in English.")
    return call_llm(provider, model, system_prompt, user, max_tokens, temperature)


# ----------------------------
# EGEL: Evidence Graph builder (lightweight)
# ----------------------------

def build_evidence_graph(anomalies: List[Dict[str, Any]], artifacts_meta: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Produces a lightweight graph snapshot (node/edge lists) that can be rendered even without networkx.
    Node IDs are stable strings with prefixes.
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # Nodes: anomalies
    for a in anomalies:
        nodes.append({
            "id": f"anomaly:{a['id']}",
            "type": "Anomaly",
            "label": a["id"],
            "title": a.get("title", ""),
            "severity": a.get("severity", ""),
            "resolved": bool(a.get("resolved")),
        })
        ref = a.get("itemRef", "")
        if ref:
            # Device/Permit reference node
            kind = "Permit" if a.get("type") == "EXPIRED_PERMIT" else "DeviceSerial"
            ref_id = f"{kind.lower()}:{ref}"
            nodes.append({
                "id": ref_id,
                "type": kind,
                "label": ref,
                "title": kind,
            })
            edges.append({
                "from": f"anomaly:{a['id']}",
                "to": ref_id,
                "type": "REFERS_TO",
            })

    # Nodes: artifacts
    for m in artifacts_meta:
        nodes.append({
            "id": f"artifact:{m['artifact_id']}",
            "type": "Artifact",
            "label": m["name"],
            "title": m.get("mime", ""),
            "sha256": m.get("sha256", ""),
        })

    # Optional: link artifacts to anomalies based on tags
    # (deterministic heuristic; user can refine)
    for m in artifacts_meta:
        tags = set([str(x).strip() for x in (m.get("tags") or []) if str(x).strip()])
        for a in anomalies:
            if a["id"] in tags or a.get("itemRef") in tags:
                edges.append({
                    "from": f"artifact:{m['artifact_id']}",
                    "to": f"anomaly:{a['id']}",
                    "type": "SUPPORTS",
                })

    # Deduplicate nodes by id
    uniq: Dict[str, Dict[str, Any]] = {}
    for n in nodes:
        uniq[n["id"]] = {**uniq.get(n["id"], {}), **n}
    nodes = list(uniq.values())

    return {"nodes": nodes, "edges": edges, "generated_at": safe_now_iso(), "version": "EGEL-lite-1"}


# ----------------------------
# CGFS: Forensics extraction (lightweight)
# ----------------------------

def extract_signals_from_text(text: str) -> Dict[str, Any]:
    """
    Deterministic forensics signals from extracted text.
    This does NOT claim counterfeit; it flags inconsistencies/suspicious markers.
    """
    serials = sorted(set(re.findall(r"\b[A-Z]{2,4}\d{3,8}[A-Z]\d{0,6}\b", text.upper())))
    permits = sorted(set(re.findall(r"\b0\d{5}\b", text)))
    dates = sorted(set(re.findall(r"\b20\d{2}[/-]\d{2}[/-]\d{2}\b", text)))

    # Heuristics
    signals = []
    if any("029878" in p for p in permits):
        signals.append({"signal": "Permit appears: 029878", "severity": "HIGH", "reason": "This permit is often used in expired-permit examples; verify expiry vs transaction date."})

    # Homoglyph / hidden separators suspicion (very light)
    if re.search(r"[A-Z]\s+[0-9]", text.upper()):
        signals.append({"signal": "Suspicious spacing in alphanumeric identifiers", "severity": "WARNING", "reason": "Spacing can indicate copy/paste or tampered identifiers; verify against barcode/UDI."})

    return {
        "serial_candidates": serials[:50],
        "permit_candidates": permits[:50],
        "date_candidates": dates[:50],
        "signals": signals,
        "generated_at": safe_now_iso(),
    }


# ----------------------------
# ROPG: Recall simulation (deterministic)
# ----------------------------

def recall_simulate(distributions: "pd.DataFrame", anomalies: List[Dict[str, Any]], scope: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic impact calculation:
    - If scope includes serial_norm list -> filter distributions by normalized serial
    - If scope includes permit list -> filter by permitNo
    - If scope includes date window -> filter deliveryDate
    """
    df = distributions.copy()
    df["serial_norm"] = df["serialNo"].apply(normalize_serial)

    serials = set(scope.get("serial_norms") or [])
    permits = set(scope.get("permits") or [])

    start = parse_yyyymmdd(scope.get("start_date", "") or "")
    end = parse_yyyymmdd(scope.get("end_date", "") or "")

    mask = pd.Series([True] * len(df))
    if serials:
        mask &= df["serial_norm"].isin(list(serials))
    if permits:
        mask &= df["permitNo"].astype(str).isin(list(permits))
    if start or end:
        def in_window(d):
            dd = parse_yyyymmdd(str(d))
            if dd is None:
                return False
            if start and dd < start:
                return False
            if end and dd > end:
                return False
            return True
        mask &= df["deliveryDate"].apply(in_window)

    impacted = df[mask].copy()
    impacted_targets = impacted["target"].astype(str).value_counts().to_dict()
    impacted_serials = sorted(set(impacted["serial_norm"].astype(str).tolist()))

    # Tie to triggering anomalies
    trigger_ids = scope.get("trigger_anomaly_ids") or []
    trigger = [a for a in anomalies if a["id"] in trigger_ids] if trigger_ids else []

    return {
        "plan_id": f"RECALL-{uuid.uuid4().hex[:8].upper()}",
        "generated_at": safe_now_iso(),
        "scope": scope,
        "trigger_anomalies": trigger,
        "impacted_rows": int(len(impacted)),
        "impacted_targets": impacted_targets,
        "impacted_serial_norms": impacted_serials,
        "notes": "Deterministic simulation only; AI playbook drafting is optional.",
    }


# ----------------------------
# UI components
# ----------------------------

def provider_key_ui(provider: str) -> None:
    env_k = env_key_for(provider)
    if env_k:
        st.markdown(f"<span class='wow-badge'>{t('provider_configured')}</span>", unsafe_allow_html=True)
        return

    st.markdown(f"<span class='wow-badge'>{t('provider_missing')}</span>", unsafe_allow_html=True)
    st.session_state.setdefault("api_keys", {})
    with st.expander(f"{provider} API Key", expanded=False):
        k = st.text_input(f"Enter {provider} API key", type="password", key=f"key_input_{provider}")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(f"Save {provider} key", key=f"save_key_{provider}"):
                if k and len(k) >= 8:
                    st.session_state.api_keys[provider] = k.strip()
                    st.success("Saved in session (not displayed).")
                else:
                    st.error("Key looks too short.")
        with col2:
            if st.button(f"Clear {provider} key", key=f"clear_key_{provider}"):
                st.session_state.api_keys.pop(provider, None)
                st.info("Cleared from session.")


def render_live_logs() -> None:
    with st.expander("Live Log", expanded=False):
        if st.session_state.logs:
            st.code("\n".join(st.session_state.logs[-200:]), language="text")
        else:
            st.caption("No logs yet.")


def render_ai_traces() -> None:
    with st.expander("AI Trace (AIET)", expanded=False):
        traces = st.session_state.ai_traces[-200:]
        if not traces:
            st.caption("No AI traces yet.")
            return
        st.json(traces)


def safe_df_view(df: "pd.DataFrame", title: str, max_rows: int = 200) -> None:
    st.subheader(title)
    if df is None or len(df) == 0:
        st.info("No data.")
        return
    st.dataframe(df.head(max_rows), use_container_width=True)


# ----------------------------
# Main app
# ----------------------------

def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    init_session()

    palette = PANTONE_STYLES[st.session_state.style_idx]
    inject_css(st.session_state.theme, palette)

    st.title(APP_TITLE)
    st.caption(f"{t('app_subtitle')}  |  {APP_VERSION}")

    # Sidebar
    with st.sidebar:
        st.header(t("sidebar_ui"))

        st.session_state.lang = st.selectbox("Language", LANGS, index=LANGS.index(st.session_state.lang))
        st.session_state.theme = st.selectbox("Theme", THEMES, index=THEMES.index(st.session_state.theme))

        style_names = [f"{i+1}. {p['name']}" for i, p in enumerate(PANTONE_STYLES)]
        st.session_state.style_idx = st.selectbox("PANTONE Style", list(range(len(PANTONE_STYLES))),
                                                  format_func=lambda i: style_names[i],
                                                  index=int(st.session_state.style_idx))
        if st.button("Jackpot 🎲 (Random Style)"):
            st.session_state.style_idx = int(time.time()) % len(PANTONE_STYLES)
            st.rerun()

        st.divider()
        st.header(t("sidebar_security"))

        st.session_state.provider = st.selectbox("Provider", PROVIDERS, index=PROVIDERS.index(st.session_state.provider))
        provider = st.session_state.provider
        models = MODEL_CATALOG.get(provider, [])
        # Keep model if possible; else default first
        if st.session_state.model not in models:
            st.session_state.model = models[0] if models else DEFAULT_MODEL
        st.session_state.model = st.selectbox("Model", models, index=models.index(st.session_state.model) if st.session_state.model in models else 0)

        st.session_state.max_tokens = st.number_input("max_tokens", min_value=256, max_value=32000, value=int(st.session_state.max_tokens), step=256)
        st.session_state.temperature = st.slider("temperature", min_value=0.0, max_value=1.0, value=float(st.session_state.temperature), step=0.05)

        provider_key_ui(provider)

        st.divider()
        st.header(t("sidebar_data"))
        if st.button("Reset session (safe)"):
            # Preserve env keys; clear session-only artifacts
            keep_lang = st.session_state.lang
            keep_theme = st.session_state.theme
            keep_style = st.session_state.style_idx
            st.session_state.clear()
            init_session()
            st.session_state.lang = keep_lang
            st.session_state.theme = keep_theme
            st.session_state.style_idx = keep_style
            st.rerun()

        render_live_logs()
        render_ai_traces()

    # Tabs
    tab_titles = I18N["tabs"][st.session_state.lang]
    tabs = st.tabs(tab_titles)

    ensure_dataframes()

    # ---------------- Dashboard ----------------
    with tabs[0]:
        st.markdown("<div class='wow-panel'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])
        with col1:
            st.subheader("Compliance Score")
            if not st.session_state.anomalies:
                st.session_state.anomalies = detect_anomalies(
                    st.session_state.distributions_df,
                    st.session_state.purchases_df,
                    st.session_state.permit_expiry_map,
                )
            st.session_state.compliance_score = compute_compliance_score(st.session_state.anomalies)
            score = st.session_state.compliance_score
            st.metric("Score", f"{score}/100")
            st.progress(score / 100.0)

        with col2:
            st.subheader("Anomalies")
            open_cnt = sum(1 for a in st.session_state.anomalies if not a.get("resolved"))
            st.metric("Open", open_cnt)
            st.metric("Total", len(st.session_state.anomalies))

        with col3:
            st.subheader("Evidence")
            st.metric("Artifacts", len(st.session_state.artifacts))
            st.metric("AI Traces", len(st.session_state.ai_traces))

        with col4:
            st.subheader("WOW Modules")
            st.write("- EGEL: Evidence Graph")
            st.write("- CGFS: Forensics Studio")
            st.write("- ROPG: Recall Console")

        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("Quick Actions")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Re-run anomaly detection"):
                st.session_state.anomalies = detect_anomalies(
                    st.session_state.distributions_df,
                    st.session_state.purchases_df,
                    st.session_state.permit_expiry_map,
                )
                st.session_state.compliance_score = compute_compliance_score(st.session_state.anomalies)
                log("Anomaly detection re-run.")
                st.success("Done.")
        with c2:
            if st.button("Build Evidence Graph snapshot (EGEL)"):
                metas = [v["meta"] for v in st.session_state.artifacts.values()]
                st.session_state.graph_snapshot = build_evidence_graph(st.session_state.anomalies, metas)
                log("Evidence graph snapshot generated.")
                st.success("Graph snapshot generated.")
        with c3:
            if st.button("Create Recall Simulation (default scope)"):
                # Default: include all CRITICAL anomalies refs
                serials = [a.get("itemRef") for a in st.session_state.anomalies if a.get("type") != "EXPIRED_PERMIT" and a.get("severity") == "CRITICAL"]
                permits = [a.get("itemRef") for a in st.session_state.anomalies if a.get("type") == "EXPIRED_PERMIT"]
                scope = {
                    "trigger_anomaly_ids": [a["id"] for a in st.session_state.anomalies if a.get("severity") == "CRITICAL"],
                    "serial_norms": [normalize_serial(x) for x in serials if x],
                    "permits": [str(x) for x in permits if x],
                    "start_date": "",
                    "end_date": "",
                }
                plan = recall_simulate(st.session_state.distributions_df, st.session_state.anomalies, scope)
                st.session_state.recall_plans.append(plan)
                log(f"Recall simulation created: {plan['plan_id']}")
                st.success(f"Created {plan['plan_id']}")

    # ---------------- GIS Map ----------------
    with tabs[1]:
        st.subheader("GIS (Leaflet-like) Overview")
        if pdk is None:
            st.warning("pydeck not installed. Showing station table only.")
        # Minimal station set (demo); extend as needed
        stations = [
            {"id": "N1", "name": "台大醫院", "type": "Medical Center", "region": "North", "lat": 25.040, "lng": 121.518},
            {"id": "N2", "name": "林口長庚", "type": "Medical Center", "region": "North", "lat": 25.061, "lng": 121.366},
            {"id": "S1", "name": "奇美永康", "type": "Medical Center", "region": "South", "lat": 23.047, "lng": 120.257},
        ]
        df = st.session_state.distributions_df.copy()
        df["serial_norm"] = df["serialNo"].apply(normalize_serial)
        station_activity = {}
        for s in stations:
            name = s["name"]
            station_activity[name] = int((df["target"].astype(str).str.contains(name)).sum())
        map_rows = []
        for s in stations:
            map_rows.append({**s, "itemsCount": station_activity.get(s["name"], 0)})
        map_df = pd.DataFrame(map_rows)

        if pdk is not None:
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position="[lng, lat]",
                get_radius=2500,
                get_fill_color="[itemsCount*40, 100, 180, 160]",
                pickable=True,
            )
            view_state = pdk.ViewState(latitude=23.7, longitude=121.0, zoom=6.6, pitch=0)
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "{name}\n{type}\nitemsCount: {itemsCount}"},
                map_style="mapbox://styles/mapbox/light-v10" if st.session_state.theme == "Sleek Light" else "mapbox://styles/mapbox/dark-v10",
            )
            st.pydeck_chart(deck, use_container_width=True)

        st.dataframe(map_df, use_container_width=True)

    # ---------------- Ledger & Anomalies ----------------
    with tabs[2]:
        st.subheader("Dataset Manager + Ledger + Anomaly List")

        with st.expander("Upload datasets (CSV/JSON) — Distributions & Purchases", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                up = st.file_uploader("Upload Distributions (CSV/JSON)", type=["csv", "json"], key="upl_dist")
                if up is not None:
                    b = up.getvalue()
                    try:
                        if up.name.lower().endswith(".csv"):
                            st.session_state.distributions_df = pd.read_csv(io.BytesIO(b))
                        else:
                            st.session_state.distributions_df = pd.read_json(io.BytesIO(b))
                        log(f"Distributions uploaded: {up.name}")
                        st.success("Loaded distributions.")
                    except Exception as e:
                        st.error(f"Failed to load: {e}")

            with col2:
                up2 = st.file_uploader("Upload Purchases (CSV/JSON)", type=["csv", "json"], key="upl_pur")
                if up2 is not None:
                    b = up2.getvalue()
                    try:
                        if up2.name.lower().endswith(".csv"):
                            st.session_state.purchases_df = pd.read_csv(io.BytesIO(b))
                        else:
                            st.session_state.purchases_df = pd.read_json(io.BytesIO(b))
                        log(f"Purchases uploaded: {up2.name}")
                        st.success("Loaded purchases.")
                    except Exception as e:
                        st.error(f"Failed to load: {e}")

            st.caption("Tip: After uploading, re-run anomaly detection for refreshed results.")

        colA, colB = st.columns([1.2, 1])
        with colA:
            safe_df_view(st.session_state.distributions_df, "Distribution Ledger (出貨申報大帳)")
        with colB:
            safe_df_view(st.session_state.purchases_df, "Purchase Ledger (醫院驗收對帳)")

        st.divider()
        st.subheader("Anomalies")
        if st.button("Detect anomalies now"):
            st.session_state.anomalies = detect_anomalies(
                st.session_state.distributions_df,
                st.session_state.purchases_df,
                st.session_state.permit_expiry_map,
            )
            st.session_state.compliance_score = compute_compliance_score(st.session_state.anomalies)
            log("Anomaly detection executed from Ledger tab.")

        if not st.session_state.anomalies:
            st.info("No anomalies detected yet. Click 'Detect anomalies now'.")
        else:
            for a in st.session_state.anomalies:
                with st.container(border=True):
                    cols = st.columns([1.2, 1, 1, 1])
                    cols[0].markdown(f"**{a['id']}** — `{a['type']}` — **{a['severity']}**")
                    cols[1].markdown(f"Ref: `{a.get('itemRef','')}`")
                    cols[2].markdown("✅ Resolved" if a.get("resolved") else "❗ Open")
                    if cols[3].button("Toggle Resolve", key=f"res_{a['id']}"):
                        a["resolved"] = not a.get("resolved")
                        st.session_state.compliance_score = compute_compliance_score(st.session_state.anomalies)
                        log(f"Anomaly {a['id']} resolved={a['resolved']}")
                        st.rerun()
                    st.write(a.get("title", ""))
                    st.caption(a.get("description", ""))

    # ---------------- Agentic Workbench ----------------
    with tabs[3]:
        st.subheader("Agentic Workbench — Run agents one by one, edit output between steps")

        # Parse/standardize agents
        agents, errors, std_yaml = standardize_agents_yaml(st.session_state.agents_yaml_text)
        if errors:
            st.warning("agents.yaml has issues; standardized version is generated. Please review in Config tab.")
            for e in errors:
                st.write(f"- {e}")
        st.session_state.agents = agents or []

        # Context builder
        dist = st.session_state.distributions_df
        pur = st.session_state.purchases_df
        anomalies = st.session_state.anomalies or []
        dist_sample = dist.head(30).to_dict(orient="records")
        pur_sample = pur.head(30).to_dict(orient="records")

        default_prompt = "請針對目前資料集的異常（重複序號/時間倒置/過期許可）提出稽核摘要、證據需求與行動建議。"
        user_prompt = st.text_area("Prompt (modifiable)", value=default_prompt, height=120)

        st.caption("WOW Execution Visualization: progress bar + status + live log updates.")

        if st.button("Run agents sequentially"):
            st.session_state.agent_outputs = []
            prog = st.progress(0.0)
            status = st.status("Running agent pipeline...", expanded=True)

            n = max(1, len(st.session_state.agents))
            prev_output = ""

            for i, agent in enumerate(st.session_state.agents):
                agent_name = agent.get("name", f"Agent{i+1}")
                guardrails = agent.get("guardrails") or []
                system = build_system_prompt(agent.get("system", ""), st.session_state.skill_md_text, st.session_state.lang, guardrails)

                # Provide grounded context, but keep it bounded
                ctx = {
                    "distributions_sample": dist_sample,
                    "purchases_sample": pur_sample,
                    "anomalies": anomalies[:25],
                    "previous_agent_output": prev_output[:8000],  # cap
                }
                payload = f"""[CONTEXT_JSON]
{json.dumps(ctx, ensure_ascii=False, indent=2)}

[USER_PROMPT]
{user_prompt}

[AGENT_GOAL]
{agent.get('goal','')}
"""
                status.write(f"→ Running: **{agent_name}**")
                log(f"Agent start: {agent_name}")

                out = call_llm(
                    st.session_state.provider,
                    st.session_state.model,
                    system_prompt=system,
                    user_prompt=payload,
                    max_tokens=int(st.session_state.max_tokens),
                    temperature=float(st.session_state.temperature),
                )

                st.session_state.agent_outputs.append({
                    "agent_name": agent_name,
                    "output": out,
                    "edited_output": out,
                    "ts": safe_now_iso(),
                })
                prev_output = out
                prog.progress((i + 1) / n)
                log(f"Agent done: {agent_name}")

            status.update(label="Pipeline completed.", state="complete")
            st.success("All agents completed. You can edit outputs below and re-run downstream agents manually if needed.")

        # Editing outputs + re-run selected agent(s) with edited upstream
        if st.session_state.agent_outputs:
            st.divider()
            st.subheader("Agent Outputs (editable)")
            for idx, item in enumerate(st.session_state.agent_outputs):
                with st.expander(f"{idx+1}. {item['agent_name']}", expanded=(idx == 0)):
                    view = st.radio("View", ["Markdown", "Text"], horizontal=True, key=f"view_{idx}")
                    edited = st.text_area("Editable output (will be used as input to next agent)", value=item["edited_output"], height=240, key=f"edit_{idx}")
                    st.session_state.agent_outputs[idx]["edited_output"] = edited

                    if view == "Markdown":
                        st.markdown(edited, unsafe_allow_html=True)
                    else:
                        st.code(edited, language="text")

            st.divider()
            st.subheader("Re-run from a specific agent (uses edited previous output)")
            start_idx = st.number_input("Start from agent #", min_value=1, max_value=len(st.session_state.agents), value=1, step=1)
            if st.button("Re-run from selected agent onward"):
                # Use edited output from previous agent as context
                agents = st.session_state.agents
                outputs = st.session_state.agent_outputs
                i0 = int(start_idx) - 1

                prev = outputs[i0 - 1]["edited_output"] if i0 > 0 else ""
                prog = st.progress(0.0)
                status = st.status("Re-running...", expanded=True)

                for j in range(i0, len(agents)):
                    agent = agents[j]
                    agent_name = agent.get("name", f"Agent{j+1}")
                    guardrails = agent.get("guardrails") or []
                    system = build_system_prompt(agent.get("system", ""), st.session_state.skill_md_text, st.session_state.lang, guardrails)

                    ctx = {
                        "distributions_sample": dist_sample,
                        "purchases_sample": pur_sample,
                        "anomalies": anomalies[:25],
                        "previous_agent_output": prev[:8000],
                    }
                    payload = f"""[CONTEXT_JSON]
{json.dumps(ctx, ensure_ascii=False, indent=2)}

[USER_PROMPT]
{user_prompt}

[AGENT_GOAL]
{agent.get('goal','')}
"""
                    status.write(f"→ Re-running: **{agent_name}**")
                    log(f"Re-run agent start: {agent_name}")
                    out = call_llm(st.session_state.provider, st.session_state.model, system, payload,
                                   int(st.session_state.max_tokens), float(st.session_state.temperature))

                    # Update output slot (preserve chronological)
                    if j < len(outputs):
                        outputs[j]["output"] = out
                        outputs[j]["edited_output"] = out
                        outputs[j]["ts"] = safe_now_iso()
                    else:
                        outputs.append({"agent_name": agent_name, "output": out, "edited_output": out, "ts": safe_now_iso()})

                    prev = out
                    prog.progress((j - i0 + 1) / max(1, len(agents) - i0))
                    log(f"Re-run agent done: {agent_name}")

                status.update(label="Re-run completed.", state="complete")
                st.success("Re-run completed.")
                st.rerun()

    # ---------------- AI Note Keeper ----------------
    with tabs[4]:
        st.subheader("AI Note Keeper — paste or upload, transform to organized markdown + keyword highlights")

        col1, col2 = st.columns([1.1, 1])
        with col1:
            st.session_state.note_raw = st.text_area("Paste text/markdown", value=st.session_state.note_raw, height=240)

            up = st.file_uploader("Or upload (pdf / txt / md)", type=["pdf", "txt", "md"], key="note_upl")
            if up is not None:
                b = up.getvalue()
                if up.name.lower().endswith(".pdf"):
                    extracted = extract_text_from_pdf(b)
                else:
                    extracted = b.decode("utf-8", errors="replace")
                st.session_state.note_raw = extracted
                log(f"Note uploaded: {up.name}")
                st.success("Loaded into Note input.")

        with col2:
            st.markdown("<div class='wow-panel'>", unsafe_allow_html=True)
            st.caption("AI Magics (6) + WOW (3)")
            magic = st.selectbox(
                "Magic",
                [
                    "Organize Markdown",
                    "Summarize",
                    "Action Items",
                    "Flashcards Q&A",
                    "Compliance Tone Rewrite",
                    "Translate (EN<->ZH-TW)",
                    "WOW: Evidence Memo (EGEL)",
                    "WOW: Counterfeit Suspicion Signals (CGFS)",
                    "WOW: Recall Playbook (ROPG)",
                ],
            )
            if st.button("Run Magic"):
                if not st.session_state.note_raw.strip():
                    st.error("Note is empty.")
                else:
                    out = ai_magic_transform(
                        st.session_state.note_raw,
                        mode=magic,
                        provider=st.session_state.provider,
                        model=st.session_state.model,
                        max_tokens=int(st.session_state.max_tokens),
                        temperature=float(st.session_state.temperature),
                        lang=st.session_state.lang,
                    )
                    st.session_state.note_md = out
                    log(f"AI Magic executed: {magic}")
                    st.success("Done.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("Keyword Highlighting (Coral default) — AI Keywords feature")
        kws_auto = simple_keyword_extract(st.session_state.note_md or st.session_state.note_raw, top_k=12)
        kws_text = st.text_input("Keywords (comma-separated)", value=", ".join(kws_auto))
        color = st.color_picker("Keyword color", value="#FF7F50")  # coral
        kw_list = [k.strip() for k in kws_text.split(",") if k.strip()]

        view = st.radio("Note view", ["Markdown", "Text"], horizontal=True, key="note_view")
        editable = st.text_area("Editable note output", value=st.session_state.note_md or st.session_state.note_raw, height=280, key="note_edit")
        # Persist edits
        st.session_state.note_md = editable

        if view == "Markdown":
            rendered = highlight_keywords_markdown(editable, kw_list, color=color)
            st.markdown(rendered, unsafe_allow_html=True)
        else:
            st.code(editable, language="text")

        st.divider()
        download_button("Download note.md", data=(st.session_state.note_md or "").encode("utf-8"),
                        file_name="note.md", mime="text/markdown")

    # ---------------- Forensics Studio (CGFS) ----------------
    with tabs[5]:
        st.subheader("Counterfeit & Grey-Market Forensics Studio (CGFS) — upload evidence, extract signals")
        st.caption("This module flags *signals* and recommends verification. It does not make definitive counterfeit claims.")

        up = st.file_uploader("Upload evidence (pdf/txt/md/png/jpg)", type=["pdf", "txt", "md", "png", "jpg", "jpeg"], key="cgfs_upl")
        tags = st.text_input("Optional tags (comma-separated): e.g., ANOM-XXXX, RNJ146480G, 029878", value="")
        tag_list = [x.strip() for x in tags.split(",") if x.strip()]

        if up is not None and st.button("Ingest evidence"):
            data = up.getvalue()
            mime = up.type or "application/octet-stream"
            meta = upsert_artifact(up.name, mime, data, tags=tag_list)
            st.success(f"Ingested artifact_id={meta['artifact_id']}")

        # Select artifact
        metas = [v["meta"] for v in st.session_state.artifacts.values()]
        if not metas:
            st.info("No artifacts uploaded yet.")
        else:
            pick = st.selectbox("Select artifact", metas, format_func=lambda m: f"{m['name']}  ({m['artifact_id'][:8]})")
            art = st.session_state.artifacts[pick["artifact_id"]]
            meta = art["meta"]
            data = art["data"]

            st.markdown("<div class='wow-panel'>", unsafe_allow_html=True)
            st.write(f"**artifact_id:** {meta['artifact_id']}")
            st.write(f"**sha256:** `{meta['sha256']}`")
            st.write(f"**mime:** {meta['mime']}  |  **size:** {meta['size']} bytes")
            st.write(f"**tags:** {', '.join(meta.get('tags', [])) if meta.get('tags') else '(none)'}")
            st.markdown("</div>", unsafe_allow_html=True)

            # Extract text
            extracted = ""
            if meta["mime"] == "application/pdf" or meta["name"].lower().endswith(".pdf"):
                extracted = extract_text_from_pdf(data)
            elif meta["mime"].startswith("text/") or meta["name"].lower().endswith((".txt", ".md")):
                extracted = data.decode("utf-8", errors="replace")
            else:
                extracted = "(Image OCR not enabled by default in this Space. Upload a PDF/text, or add OCR dependencies.)"

            st.text_area("Extracted text (read-only)", value=extracted, height=220, disabled=True)

            if st.button("Generate deterministic forensics signals"):
                sig = extract_signals_from_text(extracted)
                meta["status"] = "EXTRACTED"
                meta["notes"] = "Signals generated."
                add_ai_trace({
                    "provider": "CGFS",
                    "model": "deterministic-signals-v1",
                    "status": "OK",
                    "artifact_id": meta["artifact_id"],
                    "output_fingerprint": sha256_bytes(json.dumps(sig, ensure_ascii=False).encode("utf-8")),
                })
                st.success("Signals generated.")
                st.json(sig)

                # Optional: create/update evidence graph snapshot
                if st.button("Attach to EGEL snapshot (build/refresh graph)"):
                    st.session_state.graph_snapshot = build_evidence_graph(st.session_state.anomalies, [v["meta"] for v in st.session_state.artifacts.values()])
                    log("EGEL snapshot refreshed from CGFS.")
                    st.success("EGEL snapshot refreshed.")

    # ---------------- Evidence Graph (EGEL) ----------------
    with tabs[6]:
        st.subheader("Evidence Graph & Explainability Ledger (EGEL) — evidence-grade navigation")
        if st.button("Build / Refresh EGEL snapshot"):
            metas = [v["meta"] for v in st.session_state.artifacts.values()]
            st.session_state.graph_snapshot = build_evidence_graph(st.session_state.anomalies, metas)
            log("EGEL snapshot generated/refreshed.")

        snap = st.session_state.graph_snapshot
        if not snap:
            st.info("No graph snapshot yet. Click 'Build / Refresh EGEL snapshot'.")
        else:
            st.markdown("<div class='wow-panel'>", unsafe_allow_html=True)
            st.write(f"Generated at: {snap.get('generated_at')}  |  Nodes: {len(snap.get('nodes', []))}  |  Edges: {len(snap.get('edges', []))}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.subheader("Graph Snapshot (JSON)")
            st.json(snap)

            st.divider()
            st.subheader("Explain an anomaly (AI memo with citations placeholders)")
            anom_ids = [a["id"] for a in (st.session_state.anomalies or [])]
            if not anom_ids:
                st.info("No anomalies available.")
            else:
                sel = st.selectbox("Select anomaly", anom_ids)
                anom = next(a for a in st.session_state.anomalies if a["id"] == sel)

                metas = [v["meta"] for v in st.session_state.artifacts.values()]
                memo_ctx = {
                    "anomaly": anom,
                    "related_artifacts": [m for m in metas if (anom.get("id") in (m.get("tags") or []) or anom.get("itemRef") in (m.get("tags") or []))],
                    "compliance_score": st.session_state.compliance_score,
                }
                prompt = f"""Draft an evidence-grade memo with explicit citations placeholders.
Include:
- Summary
- Observations
- Evidence list (artifact_id, sha256)
- Assumptions & uncertainties
- Next evidence request checklist
- Recommended regulator actions

Context JSON:
{json.dumps(memo_ctx, ensure_ascii=False, indent=2)}
"""
                if st.button("Generate memo (LLM or fallback)"):
                    out = call_llm(
                        st.session_state.provider,
                        st.session_state.model,
                        system_prompt="You write professional regulatory memos with audit-grade structure and citations placeholders.",
                        user_prompt=prompt,
                        max_tokens=int(st.session_state.max_tokens),
                        temperature=float(st.session_state.temperature),
                    )
                    st.markdown(out, unsafe_allow_html=True)

                    download_button("Download memo.md", out.encode("utf-8"), f"evidence_memo_{sel}.md", "text/markdown")

    # ---------------- Recall Console (ROPG) ----------------
    with tabs[7]:
        st.subheader("Recall Console & Playbook Generator (ROPG) — deterministic simulation + optional AI playbook")

        anomalies = st.session_state.anomalies or []
        if not anomalies:
            st.info("No anomalies yet. Run anomaly detection first.")
        else:
            open_anoms = [a for a in anomalies if not a.get("resolved")]
            st.write(f"Open anomalies: **{len(open_anoms)}**")

            trigger = st.multiselect("Trigger anomalies", options=[a["id"] for a in anomalies], default=[a["id"] for a in open_anoms[:3]])
            scope_serials = []
            scope_permits = []
            for a in anomalies:
                if a["id"] in trigger:
                    if a["type"] == "EXPIRED_PERMIT":
                        scope_permits.append(str(a.get("itemRef", "")))
                    else:
                        scope_serials.append(normalize_serial(a.get("itemRef", "")))

            st.markdown("**Scope rules**")
            c1, c2, c3 = st.columns(3)
            with c1:
                use_serial = st.checkbox("Include serial_norm scope", value=True)
            with c2:
                use_permit = st.checkbox("Include permit scope", value=True)
            with c3:
                use_date_window = st.checkbox("Use delivery date window", value=False)

            start_date = st.text_input("Start date (YYYY-MM-DD)", value="")
            end_date = st.text_input("End date (YYYY-MM-DD)", value="")

            scope = {
                "trigger_anomaly_ids": trigger,
                "serial_norms": scope_serials if use_serial else [],
                "permits": scope_permits if use_permit else [],
                "start_date": start_date if use_date_window else "",
                "end_date": end_date if use_date_window else "",
            }

            if st.button("Run deterministic impact simulation"):
                plan = recall_simulate(st.session_state.distributions_df, anomalies, scope)
                st.session_state.recall_plans.append(plan)
                log(f"Recall simulation executed: {plan['plan_id']}")
                st.success(f"Created {plan['plan_id']}")
                st.json(plan)

            st.divider()
            st.subheader("Generate AI Playbook (optional)")
            if st.session_state.recall_plans:
                pick = st.selectbox("Select recall plan", st.session_state.recall_plans, format_func=lambda p: f"{p['plan_id']} — impacted_rows={p['impacted_rows']}")
                prompt = f"""Create a regulator-ready recall playbook in Markdown.
Must include:
- Executive summary
- Triggering anomalies (IDs)
- Scope definition rules
- Affected institutions table
- Phased action plan (containment/verification/communication/remediation/closure)
- Evidence request checklist
- Closure criteria (measurable)

Recall plan JSON:
{json.dumps(pick, ensure_ascii=False, indent=2)}
"""
                if st.button("Draft playbook (LLM or fallback)"):
                    out = call_llm(
                        st.session_state.provider,
                        st.session_state.model,
                        system_prompt="You are a TFDA regulatory operations lead drafting recall playbooks.",
                        user_prompt=prompt,
                        max_tokens=int(st.session_state.max_tokens),
                        temperature=float(st.session_state.temperature),
                    )
                    st.markdown(out, unsafe_allow_html=True)
                    download_button("Download playbook.md", out.encode("utf-8"), f"recall_playbook_{pick['plan_id']}.md", "text/markdown")
            else:
                st.info("No recall plans yet. Run a simulation first.")

    # ---------------- Config files: agents.yaml / SKILL.md ----------------
    with tabs[8]:
        st.subheader("Config Module — paste/upload/download/modify agents.yaml and SKILL.md")
        st.caption("Uploads are standardized before import; YAML errors are shown. No code execution occurs.")

        left, right = st.columns(2)

        with left:
            st.markdown("### agents.yaml")
            upl = st.file_uploader("Upload agents.yaml", type=["yaml", "yml"], key="upl_agents_yaml")
            if upl is not None:
                raw = upl.getvalue().decode("utf-8", errors="replace")
                agents, errors, std_yaml = standardize_agents_yaml(raw)
                st.session_state.agents_yaml_text = std_yaml
                st.session_state.agents = agents or []
                if errors:
                    st.warning("Uploaded YAML had issues; imported standardized version.")
                    for e in errors:
                        st.write(f"- {e}")
                else:
                    st.success("Imported and standardized.")
                log(f"agents.yaml uploaded and standardized: {upl.name}")

            st.session_state.agents_yaml_text = st.text_area("Edit agents.yaml", value=st.session_state.agents_yaml_text, height=320)
            if st.button("Validate & Standardize agents.yaml"):
                agents, errors, std_yaml = standardize_agents_yaml(st.session_state.agents_yaml_text)
                st.session_state.agents_yaml_text = std_yaml
                st.session_state.agents = agents or []
                if errors:
                    st.warning("Validation found issues (standardized output applied).")
                    for e in errors:
                        st.write(f"- {e}")
                else:
                    st.success("Valid.")
                log("agents.yaml validated/standardized in-app.")

            download_button("Download agents.yaml", st.session_state.agents_yaml_text.encode("utf-8"), "agents.yaml", "text/yaml")

        with right:
            st.markdown("### SKILL.md")
            upl2 = st.file_uploader("Upload SKILL.md", type=["md", "txt"], key="upl_skill_md")
            if upl2 is not None:
                raw = upl2.getvalue().decode("utf-8", errors="replace")
                st.session_state.skill_md_text = raw
                log(f"SKILL.md uploaded: {upl2.name}")
                st.success("Imported.")

            st.session_state.skill_md_text = st.text_area("Edit SKILL.md", value=st.session_state.skill_md_text, height=320)
            download_button("Download SKILL.md", st.session_state.skill_md_text.encode("utf-8"), "SKILL.md", "text/markdown")

    # Footer
    st.divider()
    st.caption("Security note: API keys entered in UI are stored only in Streamlit session_state and are not printed or logged.")


if __name__ == "__main__":
    main()
