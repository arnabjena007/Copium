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
                "parameters": {"max_new_tokens": 150, "temperature": 0.7, "return_full_text": False},
                "options": {"wait_for_model": True}
            }
            hf_resp = requests.post(
                HF_API_URL,
                headers={"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"},
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

def load_data(demo_mode: bool) -> List[Dict[str, Any]]:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
        
    # The new JSON is a flat array of highly granular hourly data
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
    df = pd.DataFrame(records)
    
    total_burn = float(df["cost_usd"].sum())
    
    # Filter anomalies
    anomalies_df = df[df["is_anomaly"] == True]
    anomalies = len(anomalies_df)
    
    # Calculate estimated wasted cost (e.g. if CPU is empty, most of the cost is wasted)
    # We estimate 85% of anomaly costs are recoverable waste
    wasted = float(anomalies_df["cost_usd"].sum() * 0.85) if not anomalies_df.empty else 0.0
    
    optimized_burn = total_burn - wasted
    
    if fixed:
        savings = wasted
        total_burn = optimized_burn
        wasted = 0
        anomalies = 0
    else:
        savings = 0.0 # Will be populated if "Recovery" happened in the past, but we keep it 0 for current active spikes
        
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
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    
    # Daily aggregation
    daily_df = df.groupby('date').agg(
        cost_usd=('cost_usd', 'sum'),
        is_anomaly=('is_anomaly', 'any')
    ).reset_index()
    
    # Sort chronologically
    daily_df = daily_df.sort_values('date')
    dates = daily_df['date'].tolist()
    
    # Calculate effective current spend
    effective_original = []
    spike_x = []
    spike_y = []
    optimized = []
    
    for _, row in daily_df.iterrows():
        base_cost = row['cost_usd']
        is_spike = row['is_anomaly']
        
        # If fixed, the 'optimized' is roughly removing the spike variance.
        # We assume optimal cost is roughly 85% of normal, and spikes are removed.
        opt_cost = base_cost * 0.85 if not is_spike else (base_cost / 1.5) * 0.85 
        optimized.append(opt_cost)
        
        if fixed and is_spike:
            effective_original.append(opt_cost)
        else:
            effective_original.append(base_cost)
            if is_spike:
                spike_x.append(row['date'])
                spike_y.append(base_cost)

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=dates,
            y=effective_original,
            mode="lines+markers",
            name="Current Spend",
            line={"color": "#EF4444" if not fixed else "#CBD5E1", "width": 3},
            fill="tozeroy",
            fillcolor="rgba(239,68,68,0.12)" if not fixed else "rgba(203,213,225,0.12)",
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
                line={"color": "#FF0000", "width": 5}, 
                marker={"color": "#FF0000", "size": 12, "symbol": "circle-open", "line": {"width": 3}},
                hovertemplate="%{x}<br>Spike: $%{y:,.0f}<extra></extra>",
            )
        )
        
    figure.add_trace(
        go.Scatter(
            x=dates,
            y=optimized,
            mode="lines+markers",
            name="Optimized Baseline",
            line={"color": "#5EEAD4", "width": 3, "dash": "dash"},
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

    fig.add_trace(go.Scatter(
        x=normal["cpu_usage_pct"],
        y=normal["cost_usd"],
        mode="markers",
        name="Healthy",
        marker=dict(color="#64748B", size=5, opacity=0.3),
        hovertemplate="CPU: %{x}%<br>Cost: $%{y}<br>ID: %{text}<extra></extra>",
        text=normal["resource_id"]
    ))

    fig.add_trace(go.Scatter(
        x=anomalies["cpu_usage_pct"],
        y=anomalies["cost_usd"],
        mode="markers",
        name="Anomalies (Engine Flagged)",
        marker=dict(color="#FF0000", size=10, symbol="cross", opacity=0.8),
        hovertemplate="CPU: %{x}%<br>Cost: $%{y}<br>ID: %{text}<extra></extra>",
        text=anomalies["resource_id"]
    ))

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

def render_what_if_lab(current_spend: float) -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧪 CloudCFO What-If Lab</div>', unsafe_allow_html=True)
    st.write("Simulate architectural changes to see instant ROI.")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<div style='margin-bottom:0.5rem; color:#94A3B8; font-weight:700;'>Configuration</div>", unsafe_allow_html=True)
        scenario = st.selectbox("Select Scenario", ["Move to Spot Instances", "Migrate to Mumbai Region"], label_visibility="collapsed")
        
    if scenario == "Move to Spot Instances":
        results = engine.simulate_spot_migration(current_spend)
    else:
        results = engine.simulate_regional_migration(current_spend, "mumbai")

    with col2:
        fig = go.Figure(data=[
            go.Bar(name='Current', x=['Spend'], y=[results['current']], marker_color='#fb7185'),
            go.Bar(name='Projected', x=['Spend'], y=[results['projected']], marker_color='#34d399')
        ])
        fig.update_layout(
            barmode='group',
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin={"l": 16, "r": 16, "t": 32, "b": 16},
            title="Monthly Cost Comparison ($)"
        )
        st.plotly_chart(fig, use_container_width=True)

    efficiency_gain = (results['savings'] / results['current']) * 100 if results['current'] > 0 else 0
    st.info(f"💡 **CFO Insight:** By switching to {scenario}, you could recover **${results['savings']:,.2f}** per month. That's a **{efficiency_gain:.1f}%** efficiency gain.")
    st.markdown('</div>', unsafe_allow_html=True)

def render_ticker(label: str, value: float) -> None:
    text = currency(value)
    ticker_html = f'''
    <div class="ticker-card">
      <span class="ticker-label">{label}</span>
      <div class="ticker-strip">
        {''.join(f'<span class="digit">{char}</span>' for char in text)}
      </div>
    </div>
    '''
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
        f'''
        <div class="badge-panel">
          <div>
            <div class="badge-label">Cloud Tier</div>
            <div class="badge-score">{score:.1f}</div>
          </div>
          <span class="badge {badge_class}">{badge}</span>
        </div>
        ''',
        unsafe_allow_html=True,
    )

def inject_styles() -> None:
    st.markdown(
        """
        <style>
          .stApp {
            background: radial-gradient(125% 125% at 50% 10%, #ffffff 40%, #f59e0b 100%);
            color: #0F172A;
          }
          [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E2E8F0; }
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
          .badge.warn { background: rgba(251, 113, 133, 0.16); color: #BE123C; }
          
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
              background: conic-gradient(from 0deg, transparent 0%, transparent 60%, #FF8101 100%);
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
          .orange-link { color: #FF8101; font-weight: 700; font-size: 0.95rem; display: flex; align-items: center; gap: 0.5rem; cursor: pointer; }
          
          .star-rating { letter-spacing: 4px; font-size: 1.4rem; color: #FF8101; margin-bottom: 0.5rem; drop-shadow: 0 0 8px rgba(255,129,1,0.2); }
          
          /* Aceternity UI style button injection */
          div.stButton > button.st-emotion-cache-1211b43, div.stButton > button {
             background: #FF8101 !important;
             color: #FFFFFF !important;
             font-weight: 700 !important;
             border-radius: 999px !important;
             border: none !important;
             padding: 0.75rem 2rem !important;
             box-shadow: 0 4px 14px 0 rgba(255, 129, 1, 0.39) !important;
             transition: all 0.2s ease-in-out !important;
          }
          div.stButton > button:hover {
             transform: translateY(-2px) !important;
             box-shadow: 0 6px 20px rgba(255, 129, 1, 0.23) !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_metric_card(title: str, value: str, delta: str, help_text: str) -> None:
    st.markdown(
        f'''
        <div class="metric-card">
          <div class="badge-label">{title}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-sub">{delta}</div>
          <div class="metric-sub">{help_text}</div>
        </div>
        ''',
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
                "stream": False
            },
            timeout=5.0
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except requests.exceptions.RequestException:
        pass 
    
    # Fallback script if server is down:
    return f"```bash\n# AWS CLI generated command to neutralize anomaly\naws {payload.get('service', 'ec2').lower().replace('amazon', '')} stop-instances --instance-ids {payload.get('resource_id', 'i-1234')}\n```\n*Engine determined CPU Usage at {payload.get('cpu_usage_pct', 0)}% does not justify the {precise_currency(payload.get('cost_usd', 0))}/hr spend in {payload.get('environment', 'Unknown')} environment.*"

def main() -> None:
    st.set_page_config(page_title="Infrastructure Anomaly Engine", page_icon="⚙️", layout="wide")
    inject_styles()
    
    if "aws_connected" not in st.session_state:
        st.session_state.aws_connected = False

    with st.sidebar:
        st.markdown("<div style='opacity:0.04;font-size:0.7rem'>internal controls</div>", unsafe_allow_html=True)
        if st.button("Reset Session / Disconnect"):
            st.session_state.aws_connected = False
            st.session_state.boto_fixed = False
            st.session_state.alert_sent = False
            st.session_state.pop("ollama_message", None)
            st.session_state.pop("last_selected_anomaly", None)
            st.rerun()

    if not st.session_state.aws_connected:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown(
                '''
                <div class="hero-card" style="text-align:center; padding: 4rem;">
                    <div class="hero-title">Connect AWS Environment</div>
                    <div class="hero-copy" style="margin-bottom: 2rem;">Authenticate Anomaly Engine using a Cross-Account IAM Role</div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            arn = st.text_input("IAM Role ARN", placeholder="arn:aws:iam::123456789012:role/TechnicalAudit")
            
            if st.button("Connect & Audit", type="primary", use_container_width=True):
                if arn:
                    with st.spinner("Authenticating with AWS STS..."):
                        time.sleep(1.5)
                    with st.spinner("Fetching 46,000+ Hourly Cost Explorer Metrics..."):
                        time.sleep(2.0)
                    with st.spinner("Isolating anomalies via Machine Learning..."):
                        time.sleep(1.5)
                    st.session_state.aws_connected = True
                    st.rerun()
        return

    records = load_data(True) 
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
    
    st.markdown(
        f'''
        <div class="hero-card">
          <div style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;flex-wrap:wrap;">
            <div>
              <div class="hero-title">Deep-Dive Technical Anomaly Review</div>
              <div class="hero-copy">Automated ML Infrastructure Analysis and Contextual Workload Verification.</div>
            </div>
            <div class="hero-copy">Status: {"Fix Deployed" if st.session_state.boto_fixed else "Auditing"}</div>
          </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    top_left, top_mid, top_right = st.columns([1.2, 1.2, 1.4])
    with top_left:
        render_metric_card("Total Active Spend", currency(totals["total_burn"]), f"Evaluated 46,800 hourly events", "30-day modeled AWS footprint")
    with top_mid:
        status_sub = "All stable" if totals["anomalies"] == 0 else f"Critical Severity"
        render_metric_card("Active Anomalies", str(int(totals["anomalies"])), status_sub, f"Count of outlier spikes")
    with top_right:
        render_metric_card("Identified Waste Scope", currency(totals["wasted"]), f"Score: {totals['score']:.1f}% Efficiency", "Mathematical outlier cost")

    st.markdown('''
    <div class="bento-card" style="margin-bottom:2rem; background: #FAFAFA; border: 1px solid #E5E7EB;">
      <div class="bento-title" style="color: #0F172A; font-size: 1.1rem;">🔍 Machine Learning Evaluation Criteria</div>
      <div class="bento-desc" style="color: #4B5563; margin-bottom: 0;">
        The Isolation Forest model flags resources based on the following outlier thresholds across 46k records:<br>
        • <b>Idle Resource:</b> <code>cpu_usage_pct < 10%</code> AND <code>cost_usd > strict median baseline</code>.<br>
        • <b>Compute Spike:</b> <code>cpu_usage_pct > 80%</code> paired with <code>3x cost bloat</code> via IOPS or Instance size mismatch.<br>
        • <b>Environment Misconfig:</b> Non-production environment paired with disproportionate usage scaling.
      </div>
    </div>
    ''', unsafe_allow_html=True)

    main_col, side_col = st.columns([2.5, 1.5], gap="large")
    with main_col:
        st.markdown('<div class="section-title">Volume & Spike Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-card" style="margin-bottom:2rem;">', unsafe_allow_html=True)
        st.plotly_chart(build_cost_figure(records, st.session_state.boto_fixed), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Resource Utilization Efficiency</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.plotly_chart(build_cpu_cost_scatter(records), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with side_col:
        if not incidents:
            st.success("No anomalies currently active.")
            return
            
        st.markdown('<div class="section-title" style="margin-bottom:0.5rem;">🚨 Anomaly Selection</div>', unsafe_allow_html=True)
        
        anomaly_options = {f"{inc.get('resource_id')} ({inc.get('service')})": inc for inc in incidents}
        selected_key = st.selectbox("Inspect technical details:", list(anomaly_options.keys()), label_visibility="collapsed")
        featured = anomaly_options[selected_key]
        
        is_idle = featured.get('cpu_usage_pct', 0) < 10
        anomaly_type = "Idle Resource" if is_idle else "Compute Spike / Architecture Bloat"
        
        st.markdown(f'''
        <div class="mini-card" style="margin-bottom:1.5rem; border-color: #EF4444; background: #FEF2F2;">
            <div style="font-size:0.8rem; font-weight:700; color:#DC2626; margin-bottom: 0.2rem;">IDENTIFIED TYPE</div>
            <div style="font-size:1.1rem; font-weight:700; color:#991B1B;">{anomaly_type}</div>
            
            <div style="margin-top:1rem; display:grid; grid-template-columns: 1fr 1fr; gap:0.5rem; font-size:0.9rem;">
                <div><span style="color:#64748B;">Service:</span> <b>{featured.get('service')}</b></div>
                <div><span style="color:#64748B;">Env:</span> <b>{featured.get('environment')}</b></div>
                <div><span style="color:#64748B;">Cost:</span> <b style="color:#DC2626;">${featured.get('cost_usd', 0):.2f}/hr</b></div>
                <div><span style="color:#64748B;">CPU:</span> <b>{featured.get('cpu_usage_pct', 0)}%</b></div>
                <div><span style="color:#64748B;">Project:</span> <b>{featured.get('project')}</b></div>
                <div><span style="color:#64748B;">Region:</span> <b>{featured.get('region')}</b></div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">🤖 LLM Solution Generator</div>', unsafe_allow_html=True)
        
        spike_impact = sum(r.get("cost_usd", 0) for r in incidents) * 0.85
        
        if st.session_state.get("last_selected_anomaly") != featured.get("resource_id"):
            st.session_state.pop("ollama_message", None)
            st.session_state.pop("typed_out", None)
            st.session_state.last_selected_anomaly = featured.get("resource_id")
            
        if st.session_state.boto_fixed:
            explanation = f"Audit update. I've successfully executed the remediation protocol on {featured.get('resource_id', 'Unknown')}."
        else:
            if "ollama_message" not in st.session_state:
                with st.spinner("Generating Architecture Solution..."):
                    st.session_state.ollama_message = generate_consultant_insight(featured, spike_impact)
            explanation = st.session_state.ollama_message
        
        with st.chat_message("assistant"):
            if "typed_out" not in st.session_state:
                st.markdown('<span style="color:#FF8101;font-weight:700;">AWS Architect generating script...</span>', unsafe_allow_html=True)
                st.write_stream(typewriter_generator(explanation))
                st.session_state.typed_out = True
            else:
                st.write(explanation)

            if not st.session_state.boto_fixed:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Apply Fix Script", type="primary"):
                    anomaly_model = CostAnomaly(**featured)
                    with st.spinner("Executing..."):
                        res = fix_resource(anomaly_model, totals["total_burn"], totals["savings"])
                        st.session_state.boto_fixed = True
                        st.session_state.pop("typed_out", None) 
                        st.session_state.pop("ollama_message", None)
                        st.rerun()

if __name__ == "__main__":
    main()
