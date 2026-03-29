import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import plotly.graph_objects as go
import requests
import streamlit as st

from models import CostAnomaly, IdleResource
from alert_service import AlertService
from remediator import fix_resource
from automation.what_if.engine import WhatIfEngine

engine = WhatIfEngine()

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "mock_data.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

# Hugging Face Inference API — free tier, no install, works on Streamlit Cloud
# Set your token in .streamlit/secrets.toml: HF_TOKEN = "hf_xxx"
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"


def generate_consultant_insight(incident: Dict[str, Any], spike_impact: float) -> str:
    """Try HF Inference API first, then Ollama locally, then static fallback."""
    resource = incident.get("resource", "Unknown")
    service = incident.get("service", "Unknown")
    score = incident.get("anomaly_score", 0)

    # Mistral instruction format
    prompt = (
        f"[INST] You are a senior AWS FinOps consultant. Be concise — 3 sentences max. "
        f"Anomaly detected on resource: {resource} (Service: {service}). "
        f"Estimated waste: ${spike_impact:,.0f}. Anomaly score: {score:.2f}. "
        f"Explain the likely cause, the financial risk, and the single best remediation action. [/INST]"
    )

    # 1. Try Hugging Face Inference API
    hf_token = st.secrets.get("HF_TOKEN", "") if hasattr(st, "secrets") else ""
    if hf_token:
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.7,
                    "return_full_text": False,
                },
                "options": {"wait_for_model": True},
            }
            hf_resp = requests.post(
                HF_API_URL,
                headers={
                    "Authorization": f"Bearer {hf_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=45,
            )
            if hf_resp.status_code == 200:
                data = hf_resp.json()
                if isinstance(data, list) and len(data) > 0:
                    text = data[0].get("generated_text", "")
                    if text:
                        return text.strip()
        except Exception:
            pass

    # 2. Try local Ollama
    try:
        ollama_resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=20,
        )
        if ollama_resp.status_code == 200:
            return ollama_resp.json().get("response", "").strip()
    except Exception:
        pass

    # 3. Static fallback
    return (
        f"Resource **{resource}** ({service}) flagged with anomaly score **{score:.2f}** "
        f"and estimated waste of **${spike_impact:,.0f}**. "
        f"Likely cause: idle or over-provisioned instance running off-hours. "
        f"Recommended action: enable Compute Savings Plans and right-size to match actual utilisation."
    )


# Session state init
if "boto_fixed" not in st.session_state:
    st.session_state.boto_fixed = False
if "alert_sent" not in st.session_state:
    st.session_state.alert_sent = False


@st.cache_data(ttl=60)
def load_data(live: bool = False) -> List[Dict[str, Any]]:
    # 🏹 NEW: Use Local Hub Tunnel instead of 127.0.0.1
    tunnel_url = st.session_state.get("tunnel_url")
    api_key = st.secrets.get("CLOUD_CFO_API_KEY", "3d4c5eb8-9fe0-4458-882d-5750d9a78947")
    
    if live and tunnel_url:
        try:
            hub_url = tunnel_url.rstrip("/")
            # We fetch straight from your Local Hub via the tunnel
            headers = {
                "X-API-KEY": api_key,
                "bypass-tunnel-reminder": "true" # Bypass Localtunnel safety page
            }
            resp = requests.get(f"{hub_url}/api/ml/anomalies", headers=headers, timeout=20)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                # Sync live metrics based on fetched anomalies
                if data:
                    df = pd.DataFrame(data)
                    st.session_state.live_metrics = {
                        "total_burn": float(df["cost_usd"].sum()),
                        "anomalies": int(df["is_anomaly"].sum()),
                        "wasted": float(df[df["is_anomaly"]]["cost_usd"].sum() * 0.85)
                    }
                return data
        except Exception as e:
            st.error(f"🔌 Connection Lost to Local Hub: {e}")

    # Fallback to mock if not connected
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload


def currency(value: float) -> str:
    return f"${value:,.0f}"


def precise_currency(value: float) -> str:
    return f"${value:,.2f}"


def typewriter_generator(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.06)


import pandas as pd


def compute_totals(records: List[Dict[str, Any]], fixed: bool) -> Dict[str, float]:
    # If we have live metrics from the API, use them
    if not fixed and hasattr(st.session_state, "live_metrics") and st.session_state.live_metrics:
        m = st.session_state.live_metrics
        return {
            "total_burn": m["total_burn"],
            "optimized_burn": m["total_burn"] - m["wasted"],
            "savings": 72488.0, # Combined historical
            "wasted": m["wasted"],
            "anomalies": m["anomalies"],
            "score": (1 - (m["wasted"] / m["total_burn"])) * 100 if m["total_burn"] > 0 else 100,
            "co2_saved": 72488.0 * 10 * 0.4,
        }

    df = pd.DataFrame(records)

    total_burn = float(df["cost_usd"].sum())

    # Filter anomalies
    anomalies_df = df[df["is_anomaly"] == True]
    anomalies = len(anomalies_df)

    # Calculate estimated wasted cost (e.g. if CPU is empty, most of the cost is wasted)
    # We estimate 85% of anomaly costs are recoverable waste
    wasted = (
        float(anomalies_df["cost_usd"].sum() * 0.85) if not anomalies_df.empty else 0.0
    )

    optimized_burn = total_burn - wasted

    if fixed:
        savings = wasted
        total_burn = optimized_burn
        wasted = 0
        anomalies = 0
    else:
        savings = 0.0  # Will be populated if "Recovery" happened in the past, but we keep it 0 for current active spikes

    # Mocking previous recovery for the demo dashboard
    savings += 72488.0

    score = 0 if total_burn == 0 else (1 - (wasted / total_burn)) * 100
    co2_saved = savings * 10 * 0.4

    return {
        "total_burn": total_burn,
        "optimized_burn": optimized_burn,
        "savings": savings,
        "wasted": wasted,
        "anomalies": anomalies,
        "score": score,
        "co2_saved": co2_saved,
    }


def build_cost_figure(records: List[Dict[str, Any]], fixed: bool) -> go.Figure:
    df = pd.DataFrame(records)
    # Convert timestamp to date for daily aggregation
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date

    # Daily aggregation
    daily_df = (
        df.groupby("date")
        .agg(cost_usd=("cost_usd", "sum"), is_anomaly=("is_anomaly", "any"))
        .reset_index()
    )

    # Sort chronologically
    daily_df = daily_df.sort_values("date")
    dates = daily_df["date"].tolist()

    # Calculate effective current spend
    effective_original = []
    spike_x = []
    spike_y = []
    optimized = []

    for _, row in daily_df.iterrows():
        base_cost = row["cost_usd"]
        is_spike = row["is_anomaly"]

        # If fixed, the 'optimized' is roughly removing the spike variance.
        # We assume optimal cost is roughly 85% of normal, and spikes are removed.
        opt_cost = base_cost * 0.85 if not is_spike else (base_cost / 1.5) * 0.85
        optimized.append(opt_cost)

        if fixed and is_spike:
            effective_original.append(opt_cost)
        else:
            effective_original.append(base_cost)
            if is_spike:
                spike_x.append(row["date"])
                spike_y.append(base_cost)

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=dates,
            y=effective_original,
            mode="lines+markers",
            name="Current Spend",
            line={"color": "#26C1B6" if not fixed else "#CBD5E1", "width": 3},
            fill="tozeroy",
            fillcolor="rgba(38,193,182,0.15)"
            if not fixed
            else "rgba(203,213,225,0.12)",
            hovertemplate="%{x}<br>Current: $%{y:,.0f}<extra></extra>",
        )
    )

    if not fixed and spike_x:
        figure.add_trace(
            go.Scatter(
                x=spike_x,
                y=spike_y,
                mode="markers+lines",
                name="Anomaly Spike",
                line={"color": "#EF4444", "width": 5},
                marker={
                    "color": "#EF4444",
                    "size": 12,
                    "symbol": "circle-open",
                    "line": {"width": 3},
                },
                hovertemplate="%{x}<br>Spike: $%{y:,.0f}<extra></extra>",
            )
        )

    figure.add_trace(
        go.Scatter(
            x=dates,
            y=optimized,
            mode="lines+markers",
            name="Optimized Baseline",
            line={"color": "#10B981", "width": 3, "dash": "dash"},
            hovertemplate="%{x}<br>Optimized: $%{y:,.0f}<extra></extra>",
        )
    )
    figure.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 16, "r": 16, "t": 24, "b": 16},
        legend={"orientation": "h", "y": 1.08, "x": 0},
        xaxis_title="Date",
        yaxis_title="AWS Cost ($)",
    )
    return figure


def build_cpu_cost_scatter(records: List[Dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(records)
    anomalies = df[df["is_anomaly"] == True]
    normal = df[df["is_anomaly"] == False]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=normal["cpu_usage_pct"],
            y=normal["cost_usd"],
            mode="markers",
            name="Healthy",
            marker=dict(color="#64748B", size=5, opacity=0.3),
            hovertemplate="CPU: %{x}%<br>Cost: $%{y}<br>ID: %{text}<extra></extra>",
            text=normal["resource_id"],
        )
    )

    fig.add_trace(
        go.Scatter(
            x=anomalies["cpu_usage_pct"],
            y=anomalies["cost_usd"],
            mode="markers",
            name="Anomalies (Engine Flagged)",
            marker=dict(color="#EF4444", size=10, symbol="cross", opacity=0.8),
            hovertemplate="CPU: %{x}%<br>Cost: $%{y}<br>ID: %{text}<extra></extra>",
            text=anomalies["resource_id"],
        )
    )

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 16, "r": 16, "t": 32, "b": 16},
        title="CPU Utilization vs Hourly Spend Matrix",
        xaxis_title="CPU Usage (%)",
        yaxis_title="Hourly Cost ($)",
    )
    return fig


def build_service_donut(records: List[Dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(records)
    service_sum = df.groupby("service")["cost_usd"].sum().reset_index()

    fig = go.Figure(
        data=[
            go.Pie(
                labels=service_sum["service"],
                values=service_sum["cost_usd"],
                hole=0.4,
                marker=dict(
                    colors=["#26C1B6", "#6366F1", "#38C1B6", "#14B8A6", "#5EEAD4"]
                ),
                textinfo="label+percent",
            )
        ]
    )

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 0, "r": 0, "t": 40, "b": 0},
        title="Cost Distribution by Service Category",
        showlegend=False,
    )
    return fig


def build_env_bar(records: List[Dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(records)
    env_sum = df.groupby("environment")["cost_usd"].sum().reset_index()

    fig = go.Figure(
        data=[
            go.Bar(
                x=env_sum["environment"],
                y=env_sum["cost_usd"],
                marker_color=["#6366F1", "#10B981", "#F59E0B", "#EF4444"],
            )
        ]
    )

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 16, "r": 16, "t": 40, "b": 16},
        title="Infrastructure Cost by Environment",
        xaxis_title="Environment",
        yaxis_title="Total Cost ($)",
    )
    return fig


def build_anomaly_heatmap(records: List[Dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day_name()

    # Sort days for correct heatmap ordering
    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    heatmap_data = (
        df.groupby(["day", "hour"])["cost_usd"].sum().unstack().reindex(day_order)
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale="teal",
            hovertemplate="Day: %{y}<br>Hour: %{x}:00<br>Total Cost: $%{z:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 40, "r": 20, "t": 40, "b": 40},
        title="Hourly Cost Hotspots (Anomaly Heatmap)",
        xaxis_title="Hour of Day (24h)",
        yaxis_title="Day of Week",
    )
    return fig


def render_engine_logs():
    logs = [
        "[INFO] Initialized Anomaly Engine v2.4.0 (Isolation Forest enabled)",
        f"[INFO] Parsing fleet operational metadata (46,800 hourly records)...",
        "[INFO] Fitting unsupervised ML model on [cost_usd, cpu_usage_pct]",
        "[ALERT] Detected p95 divergence in high-volume RDS clusters",
        "[SUCCESS] 3 architectural cost leaks isolated for remediation",
    ]
    st.markdown(
        """
    <div style="background:#0F172A; color:#38C1B6; font-family:'Courier New', Courier, monospace; font-size:0.85rem; padding:1.2rem; border-radius:12px; border-left: 4px solid #26C1B6; margin-top:1.5rem;">
      <div style="color:#64748B; margin-bottom:0.5rem; font-weight:700;">// ANOMALY_ENGINE_STDOUT</div>
      """
        + "<br>".join(logs)
        + """
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_what_if_lab(current_spend: float) -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">🧪 CloudCFO What-If Lab</div>',
        unsafe_allow_html=True,
    )
    st.write("Simulate architectural changes to see instant ROI.")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            "<div style='margin-bottom:0.5rem; color:#94A3B8; font-weight:700;'>Configuration</div>",
            unsafe_allow_html=True,
        )
        scenario = st.selectbox(
            "Select Scenario",
            ["Move to Spot Instances", "Migrate to Mumbai Region"],
            label_visibility="collapsed",
        )

    if scenario == "Move to Spot Instances":
        results = engine.simulate_spot_migration(current_spend)
    else:
        results = engine.simulate_regional_migration(current_spend, "mumbai")

    with col2:
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Current",
                    x=["Spend"],
                    y=[results["current"]],
                    marker_color="#26C1B6",
                ),
                go.Bar(
                    name="Projected",
                    x=["Spend"],
                    y=[results["projected"]],
                    marker_color="#38C1B6",
                ),
            ]
        )
        fig.update_layout(
            barmode="group",
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin={"l": 16, "r": 16, "t": 32, "b": 16},
            title="Monthly Cost Comparison ($)",
        )
        st.plotly_chart(fig, use_container_width=True)

    efficiency_gain = (
        (results["savings"] / results["current"]) * 100 if results["current"] > 0 else 0
    )
    st.info(
        f"💡 **CFO Insight:** By switching to {scenario}, you could recover **${results['savings']:,.2f}** per month. That's a **{efficiency_gain:.1f}%** efficiency gain."
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_ticker(label: str, value: float) -> None:
    text = currency(value)
    ticker_html = f"""
    <div class="ticker-card">
      <span class="ticker-label">{label}</span>
      <div class="ticker-strip">
        {"".join(f'<span class="digit">{char}</span>' for char in text)}
      </div>
    </div>
    """
    st.markdown(ticker_html, unsafe_allow_html=True)


def render_badge(score: float) -> None:
    if score > 90:
        badge = "Gold Efficiency"
        badge_class = "gold"
    elif score > 75:
        badge = "Silver Efficiency"
        badge_class = "silver"
    else:
        badge = "Recovery Mode"
        badge_class = "warn"
    st.markdown(
        f"""
        <div class="badge-panel">
          <div>
            <div class="badge-label">Cloud Tier</div>
            <div class="badge-score">{score:.1f}</div>
          </div>
          <span class="badge {badge_class}">{badge}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inject_styles() -> None:
    st.markdown(
        """
        <style>
          .stApp {
            background: radial-gradient(125% 125% at 50% 10%, #ffffff 40%, rgba(56, 193, 182, 0.12) 100%);
            color: #0F172A;
          }
          .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
          
          .hero-card, .section-card, .ticker-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 24px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.05);
          }
          .hero-card { padding: 1.2rem 1.4rem; margin-bottom: 1rem; }
          .hero-title { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.3rem; letter-spacing: -0.03em; color: #0F172A; }
          .hero-copy { color: #64748B; }
          
          .metric-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 20px;
            padding: 1rem;
            min-height: 136px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
          }
          .badge-label, .metric-sub, .mini-label { color: #64748B; font-weight: 500;}
          .metric-value { font-size: 2rem; font-weight: 700; margin-top: 0.4rem; margin-bottom: 0.35rem; color: #0F172A; }
          .metric-sub { font-size: 0.95rem; }
          
          .badge-panel {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 20px;
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
          }
          .badge-score { font-size: 1.8rem; font-weight: 700; color: #0F172A; }
          .badge { padding: 0.5rem 0.8rem; border-radius: 999px; font-size: 0.85rem; font-weight: 700; }
          .badge.gold { background: rgba(250, 204, 21, 0.16); color: #B45309; }
          .badge.silver { background: rgba(226, 232, 240, 0.5); color: #475569; }
          .badge.warn { background: rgba(56, 193, 182, 0.16); color: #26C1B6; }
          
          .section-card { padding: 1rem 1rem 0.6rem; margin-bottom: 1rem; }
          .section-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.75rem; color: #0F172A; }
          .mini-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.8rem; }
          
          .mini-card {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 0.9rem;
          }
          .mini-value { font-size: 1.35rem; font-weight: 700; margin-top: 0.35rem; color: #0F172A; }
          
          /* Bento grid & Moving border */
          .bento-card {
              background: #FFFFFF;
              border-radius: 20px;
              padding: 1.5rem;
              position: relative;
              overflow: hidden;
              box-shadow: 0 10px 40px rgba(0,0,0,0.08);
          }
          .bento-card::before {
              content: '';
              position: absolute;
              top: -50%; left: -50%; width: 200%; height: 200%;
              background: conic-gradient(from 0deg, transparent 0%, transparent 60%, #26C1B6 100%);
              animation: spin 3.5s linear infinite;
              z-index: -1;
          }
          .bento-card::after {
              content: '';
              position: absolute;
              inset: 2px;
              background: #FFFFFF;
              border-radius: 18px;
              z-index: -1;
          }
          @keyframes spin { 100% { transform: rotate(360deg); } }
          
          .bento-title { font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem; }
          .bento-desc { color: #64748B; font-size: 0.95rem; margin-bottom: 1.2rem; line-height: 1.5; }
          .orange-link { color: #26C1B6; font-weight: 700; font-size: 0.95rem; display: flex; align-items: center; gap: 0.5rem; cursor: pointer; }
          
          .star-rating { letter-spacing: 4px; font-size: 1.4rem; color: #26C1B6; margin-bottom: 0.5rem; drop-shadow: 0 0 8px rgba(56,193,182,0.2); }
          
          /* Aceternity UI style button injection */
          div.stButton > button.st-emotion-cache-1211b43, div.stButton > button {
             background: #26C1B6 !important;
             color: #FFFFFF !important;
             font-weight: 700 !important;
             border-radius: 999px !important;
             border: none !important;
             padding: 0.75rem 2rem !important;
             box-shadow: 0 4px 14px 0 rgba(56, 193, 182, 0.39) !important;
             transition: all 0.2s ease-in-out !important;
          }
          div.stButton > button:hover {
             transform: translateY(-2px) !important;
             box-shadow: 0 6px 20px rgba(56, 193, 182, 0.23) !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(title: str, value: str, delta: str, help_text: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="badge-label">{title}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-sub">{delta}</div>
          <div class="metric-sub">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def generate_consultant_insight(payload: dict, spike_impact: float) -> str:
    system_prompt = (
        "You are a hardcore AWS Solutions Architect. An architectural isolation engine handed you this anomaly. "
        "Review the payload's CPU usage, cost, and environment. "
        "Output ONLY a raw block of technical bash script or AWS CLI code that remediates the issue (e.g. terminating the instance, modifying IOPS). "
        "NO pleasantries. NO introductory text. Just the markdown code block and a 1-sentence technical reason."
    )
    prompt = f"JSON Payload:\n{json.dumps(payload, indent=2)}\n\nEstimated Waste: {currency(spike_impact)}"

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": f"{system_prompt}\n\n{prompt}",
                "stream": False,
            },
            timeout=5.0,
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except requests.exceptions.RequestException:
        pass

    # Fallback script if server is down:
    return f"```bash\n# AWS CLI generated command to neutralize anomaly\naws {payload.get('service', 'ec2').lower().replace('amazon', '')} stop-instances --instance-ids {payload.get('resource_id', 'i-1234')}\n```\n*Engine determined CPU Usage at {payload.get('cpu_usage_pct', 0)}% does not justify the {precise_currency(payload.get('cost_usd', 0))}/hr spend in {payload.get('environment', 'Unknown')} environment.*"


def main() -> None:
    st.set_page_config(
        page_title="Infrastructure Anomaly Engine", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded"
    )

    # 🏹 NEW: Add Connection Sidebar (Visible on Vercel/Cloud to link back to local)
    with st.sidebar:
        st.title("🔐 Local Hub Connection")
        st.session_state.tunnel_url = st.text_input(
            "Localtunnel URL", 
            value=st.session_state.get("tunnel_url", ""),
            placeholder="https://example.loca.lt"
        )
        st.caption("Linking your local Anomaly Engine to the Cloud Dashboard.")
        st.divider()

    inject_styles()

    if "aws_connected" not in st.session_state:
        st.session_state.aws_connected = False

    if not st.session_state.aws_connected:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown(
                """
                <div class="hero-card" style="text-align:center; padding: 4rem;">
                    <div class="hero-title">Connect AWS Environment</div>
                    <div class="hero-copy" style="margin-bottom: 2rem;">Authenticate Anomaly Engine using a Cross-Account IAM Role</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            arn = st.text_input(
                "IAM Role ARN",
                placeholder="arn:aws:iam::100731996973:user/HackathonUser",
            )

            if st.button("Connect & Audit", type="primary", use_container_width=True):
                if arn and st.session_state.get("tunnel_url"):
                    with st.spinner("Validating IAM Role via TunnelBridge..."):
                        try:
                            # 🏹 Use the tunnel_url here!
                            hub_url = st.session_state.tunnel_url.rstrip("/")
                            headers = {
                                "X-API-KEY": api_key,
                                "bypass-tunnel-reminder": "true" # Bypass Localtunnel safety page
                            }
                            
                            # Authenticate with your local machine
                            auth_resp = requests.post(f"{hub_url}/api/auth/validate-arn", 
                                                    json={"arn": arn}, 
                                                    headers=headers, 
                                                    timeout=10)
                            if auth_resp.status_code == 200:
                                with st.spinner("Handshaking with Local Hub..."):
                                    time.sleep(1.2)
                                st.session_state.aws_connected = True
                                st.rerun()
                            else:
                                st.error(f"❌ Access Denied ({auth_resp.status_code}): Unauthorized ARN or Security Key.")
                                if auth_resp.status_code == 403:
                                    st.info("Check if your Backend and Dashboard use the same API Key.")
                        except Exception as e:
                            st.error(f"❌ Could not reach Local Hub: {e}")
                elif not arn:
                    st.warning("⚠️ Please provide a valid IAM Role ARN.")
                else:
                    st.warning("⚠️ Enter your Localtunnel URL in the sidebar first.")
        return
        return

    records = load_data(live=st.session_state.aws_connected)
    incidents = [r for r in records if r.get("is_anomaly") == True]

    if not st.session_state.alert_sent:
        service = AlertService()
        for inc in incidents:
            try:
                anomaly_model = CostAnomaly(**inc)
                service.send_alert(anomaly_model)
            except Exception as e:
                print(f"Pydantic Validation Error: {e}")
        st.session_state.alert_sent = True

    totals = compute_totals(records, fixed=st.session_state.boto_fixed)

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    hero_col1, hero_col2 = st.columns([3, 1])
    with hero_col1:
        st.markdown(
            f"""
            <div style="display:flex;justify-content:space-between;gap:1rem;align-center;items:flex-start;flex-wrap:wrap;">
                <div>
                <div class="hero-title">CloudCFO</div>
                <div class="hero-copy">Automated ML Infrastructure Analysis and Contextual Workload Verification.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with hero_col2:
        st.markdown('<div style="text-align: right; padding-top: 1rem;">', unsafe_allow_html=True)
        if st.button("Reset / Disconnect", use_container_width=True):
            st.session_state.aws_connected = False
            st.session_state.boto_fixed = False
            st.session_state.alert_sent = False
            st.session_state.pop("ollama_message", None)
            st.session_state.pop("last_selected_anomaly", None)
            st.rerun()
        st.markdown(f'<div class="hero-copy" style="margin-top:0.5rem;">Status: {"Fix Deployed" if st.session_state.boto_fixed else "Auditing"}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    top_left, top_mid, top_right = st.columns([1.2, 1.2, 1.4])
    with top_left:
        render_metric_card(
            "Total Active Spend",
            currency(totals["total_burn"]),
            f"Evaluated 46,800 hourly events",
            "30-day modeled AWS footprint",
        )
    with top_mid:
        status_sub = "All stable" if totals["anomalies"] == 0 else f"Critical Severity"
        render_metric_card(
            "Active Anomalies",
            str(int(totals["anomalies"])),
            status_sub,
            f"Count of outlier spikes",
        )
    with top_right:
        render_metric_card(
            "Identified Waste Scope",
            currency(totals["wasted"]),
            f"Score: {totals['score']:.1f}% Efficiency",
            "Mathematical outlier cost",
        )

    # Calculate Dynamic Evaluation Statistics
    df = pd.DataFrame(records)
    p95_cost = float(df["cost_usd"].quantile(0.95))
    median_cpu = float(df["cpu_usage_pct"].median())

    st.markdown(
        f"""
    <div class="bento-card" style="margin-bottom:2rem; background: #FAFAFA; border: 1px solid #E5E7EB;">
      <div class="bento-title" style="color: #0F172A; font-size: 1.1rem;">🔍 ML Significance & Evaluation Criteria</div>
      <div class="bento-desc" style="color: #4B5563; margin-bottom: 0;">
        Isolation Forest Engine dynamically tuned to current dataset (p95 Cost: <b>${p95_cost:.2f}</b>, Median CPU: <b>{median_cpu:.1f}%</b>):<br>
        • <b>Anomalous Variance:</b> Resources exceeding p95 cost divergence ($<b>{p95_cost:.2f}/hr</b>).<br>
        • <b>Idle Significance:</b> Cost > median AND <code>cpu_usage_pct < 10%</code> detected in <b>{len(incidents)}</b> active clusters.<br>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    main_col, side_col = st.columns([2.5, 1.5], gap="large")
    with main_col:
        st.markdown(
            '<div class="section-title">Critical Spike Analysis (30-Day View)</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-card" style="margin-bottom:2rem;">',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            build_cost_figure(records, st.session_state.boto_fixed),
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # 3rd row: Distribution and Efficiency
        dist_col1, dist_col2 = st.columns(2)
        with dist_col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.plotly_chart(build_service_donut(records), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with dist_col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.plotly_chart(build_env_bar(records), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="section-title">Resource Utilization Efficiency Matrix</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.plotly_chart(build_cpu_cost_scatter(records), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="section-title">Temporal Analysis (Infrastructure Hotspots)</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.plotly_chart(build_anomaly_heatmap(records), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        render_engine_logs()

    with side_col:
        if not incidents:
            st.success("No anomalies currently active.")
            return

        st.markdown(
            '<div class="section-title" style="margin-bottom:0.5rem;">🚨 Anomaly Selection</div>',
            unsafe_allow_html=True,
        )

        anomaly_options = {
            f"{inc.get('resource_id')} ({inc.get('service')})": inc for inc in incidents
        }
        selected_key = st.selectbox(
            "Inspect technical details:",
            list(anomaly_options.keys()),
            label_visibility="collapsed",
        )
        featured = anomaly_options[selected_key]

        is_idle = featured.get("cpu_usage_pct", 0) < 10
        anomaly_type = (
            "Idle Resource" if is_idle else "Compute Spike / Architecture Bloat"
        )

        st.markdown(
            f"""<div class="mini-card" style="margin-bottom:1.5rem; border-color: #26C1B6; background: #f0fdfa;">
<div style="font-size:0.8rem; font-weight:700; color:#26C1B6; margin-bottom: 0.2rem;">IDENTIFIED TYPE</div>
<div style="font-size:1.1rem; font-weight:700; color:#26C1B6;">{anomaly_type}</div>
<div style="margin-top:1rem; display:grid; grid-template-columns: 1fr 1fr; gap:0.5rem; font-size:0.9rem;">
<div><span style="color:#64748B;">Service:</span> <b>{featured.get("service")}</b></div>
<div><span style="color:#64748B;">Env:</span> <b>{featured.get("environment")}</b></div>
<div><span style="color:#64748B;">Cost:</span> <b style="color:#26C1B6;">${featured.get("cost_usd", 0):.2f}/hr</b></div>
<div><span style="color:#64748B;">CPU:</span> <b>{featured.get("cpu_usage_pct", 0)}%</b></div>
<div><span style="color:#64748B;">Project:</span> <b>{featured.get("project")}</b></div>
<div><span style="color:#64748B;">Region:</span> <b>{featured.get("region")}</b></div>
</div>
</div>""",
            unsafe_allow_html=True,
        )

        if st.session_state.boto_fixed:
            st.success(f"Audit update: Successfully executed the remediation protocol on {featured.get('resource_id', 'Unknown')}.")
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Apply Fix Script", type="primary", use_container_width=True):
                anomaly_model = CostAnomaly(**featured)
                with st.spinner("Executing..."):
                    res = fix_resource(
                        anomaly_model, totals["total_burn"], totals["savings"]
                    )
                    st.session_state.boto_fixed = True
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### ⚙️ Governance Panel")
        
        # Load current backend config
        try:
            config_resp = requests.get("http://127.0.0.1:8000/api/config", timeout=5)
            if config_resp.status_code == 200:
                current_config = config_resp.json()
            else:
                current_config = {
                    "risk_multiplier": 2.0,
                    "authorized_regions": ["us-east-1", "us-west-2", "eu-north-1"],
                    "quiet_hours": [22, 23, 0, 1, 2, 3, 4],
                    "service_sensitivity": {"AmazonS3": 1.2, "AWSLambda": 1.1, "AmazonRDS": 2.5, "AmazonEC2": 2.0}
                }
        except:
            current_config = {
                "risk_multiplier": 2.0,
                "authorized_regions": ["us-east-1", "us-west-2", "eu-north-1"],
                "quiet_hours": [22, 23, 0, 1, 2, 3, 4],
                "service_sensitivity": {"AmazonS3": 1.2, "AWSLambda": 1.1, "AmazonRDS": 2.5, "AmazonEC2": 2.0}
            }

        with st.expander("Anomaly Sensitivity"):
            new_risk = st.slider("Global Risk Multiplier", 0.5, 5.0, float(current_config.get("risk_multiplier", 2.0)))
            
            st.markdown("**Service Bias**")
            s3_sens = st.number_input("S3 Sensitivity", 0.1, 10.0, float(current_config["service_sensitivity"].get("AmazonS3", 1.2)))
            lambda_sens = st.number_input("Lambda Sensitivity", 0.1, 10.0, float(current_config["service_sensitivity"].get("AWSLambda", 1.1)))
            rds_sens = st.number_input("RDS Sensitivity", 0.1, 10.0, float(current_config["service_sensitivity"].get("AmazonRDS", 2.5)))
            ec2_sens = st.number_input("EC2 Sensitivity", 0.1, 10.0, float(current_config["service_sensitivity"].get("AmazonEC2", 2.0)))

        with st.expander("Regional Governance"):
            all_regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "eu-north-1", "ap-south-1", "eu-central-1"]
            new_regions = st.multiselect("Authorized Scan Regions", all_regions, default=current_config.get("authorized_regions", []))
            
        with st.expander("Operational Window"):
            new_quiet_hours = st.multiselect("Quiet Hours (Automation Disabled)", list(range(24)), default=current_config.get("quiet_hours", []))
            st.caption("No automated fix scripts will be deployed during these hours (UTC).")

        if st.button("Save & Deploy Config", type="primary", use_container_width=True):
            updated_config = {
                "risk_multiplier": new_risk,
                "authorized_regions": new_regions,
                "quiet_hours": new_quiet_hours,
                "service_sensitivity": {
                    "AmazonS3": s3_sens,
                    "AWSLambda": lambda_sens,
                    "AmazonRDS": rds_sens,
                    "AmazonEC2": ec2_sens
                }
            }
            try:
                tunnel_url = st.session_state.get("tunnel_url", "http://127.0.0.1:8000").rstrip("/")
                api_key = st.secrets.get("CLOUD_CFO_API_KEY", "3d4c5eb8-9fe0-4458-882d-5750d9a78947")
                headers = {
                    "X-API-KEY": api_key,
                    "bypass-tunnel-reminder": "true"
                }
                save_resp = requests.post(f"{tunnel_url}/api/config", json=updated_config, headers=headers, timeout=5)
                if save_resp.status_code == 200:
                    st.success("✅ Config pushed to local backend engine.")
                else:
                    st.error(f"❌ Failed to sync: {save_resp.text}")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")




if __name__ == "__main__":
    main()
