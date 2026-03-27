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

def generate_consultant_insight(incident: Dict[str, Any], spike_impact: float) -> str:
    """Call Ollama llama3.2 locally to generate a FinOps consultant insight."""
    prompt = (
        f"You are a senior AWS FinOps consultant. Be concise (3-4 sentences max).\n\n"
        f"Anomaly detected on resource: {incident.get('resource', 'Unknown')} "
        f"(Service: {incident.get('service', 'Unknown')}).\n"
        f"Estimated waste: ${spike_impact:,.0f}.\n"
        f"Anomaly score: {incident.get('anomaly_score', 0):.2f}.\n\n"
        f"Explain what likely caused this spike, what the financial risk is, "
        f"and recommend the single most impactful remediation action."
    )
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception:
        pass
    # Graceful fallback if Ollama is not running
    return (
        f"⚠️ AI Consultant offline (Ollama not running locally). "
        f"Resource **{incident.get('resource', 'Unknown')}** shows an anomaly score of "
        f"**{incident.get('anomaly_score', 0):.2f}** with an estimated waste of "
        f"**${spike_impact:,.0f}**. Recommended action: review EC2 rightsizing and "
        f"enable Compute Savings Plans for immediate cost recovery."
    )

# Session state init
if "boto_fixed" not in st.session_state:
    st.session_state.boto_fixed = False
if "alert_sent" not in st.session_state:
    st.session_state.alert_sent = False

def load_data(demo_mode: bool) -> Dict[str, Any]:
    if not demo_mode:
        try:
            # Phase 2: Attempt to get live metrics from local backend
            resp = requests.get("http://localhost:8000/metrics/latest", timeout=2.0)
            if resp.status_code == 200:
                return resp.json()["baseline"]
        except requests.exceptions.RequestException:
            pass # Fallback to mock data gracefully
            
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["demo" if demo_mode else "baseline"]

def currency(value: float) -> str:
    return f"${value:,.0f}"

def precise_currency(value: float) -> str:
    return f"${value:,.2f}"

def typewriter_generator(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.06)

def compute_totals(records: List[Dict[str, Any]], fixed: bool) -> Dict[str, float]:
    total_burn = 0
    optimized_burn = 0
    wasted = 0
    anomalies = 0

    for item in records:
        is_anomaly = item.get("anomaly_score", 0) >= 0.8
        actual_cost = item["cost_optimized"] if (fixed and is_anomaly) else item["cost_original"]
        
        total_burn += actual_cost
        optimized_burn += item["cost_optimized"]
        
        if not (fixed and is_anomaly):
            wasted += item.get("wasted_cost", 0)
            if is_anomaly:
                anomalies += 1

    savings = sum((item["cost_original"] - item["cost_optimized"]) for item in records)
    if fixed:
        # Increase savings by the amount recovered
        recovery = sum((item["cost_original"] - item["cost_optimized"]) for item in records if item.get("anomaly_score", 0) >= 0.8)
        savings += recovery

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
    dates = [item["date"] for item in records]
    
    # Calculate effective costs based on whether we fixed anomalies
    effective_original = []
    spike_x = []
    spike_y = []
    
    for item in records:
        is_anomaly = item.get("anomaly_score", 0) >= 0.8
        cost = item["cost_optimized"] if (fixed and is_anomaly) else item["cost_original"]
        effective_original.append(cost)
        if is_anomaly and not fixed:
            spike_x.append(item["date"])
            spike_y.append(item["cost_original"])

    optimized = [item["cost_optimized"] for item in records]

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
        # Highlight the spike in vibrant red
        figure.add_trace(
            go.Scatter(
                x=spike_x,
                y=spike_y,
                mode="markers+lines",
                name="Anomaly Spike",
                line={"color": "#FF0000", "width": 5}, # Vibrant Red
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
        xaxis_title="Day",
        yaxis_title="AWS Cost ($)",
    )
    return figure

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
        "You are a direct, senior FinOps Cloud Consultant. Analyze this anomaly JSON payload. "
        "Give exactly a 2-sentence breakdown of what is burning cash and your direct recommendation. "
        "Do not use pleasantries."
    )
    prompt = f"JSON Payload:\n{json.dumps(payload, indent=2)}\n\nSpike Value: {currency(spike_impact)}"
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": f"{system_prompt}\n\n{prompt}",
                "stream": False
            },
            timeout=3.0
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except requests.exceptions.RequestException:
        pass # Fallback if Ollama is unreachable
    
    # Fallback script if server is down:
    return f"Audit complete. I've initialized the Slack Alert Service. I found a {currency(spike_impact)} spike. Should I notify the team or fix it now?"

def main() -> None:
    st.set_page_config(page_title="CloudCFO", page_icon="🏛️", layout="wide")
    inject_styles()

    with st.sidebar:
        st.markdown("<div style='opacity:0.04;font-size:0.7rem'>internal controls</div>", unsafe_allow_html=True)
        demo_mode = st.checkbox("Demo Mode", value=False, help="Load the mock spike scenario.")
        app_url = st.text_input("Next.js Landing URL", value="http://localhost:3000")
        
        if st.button("Reset Demo"):
            st.session_state.boto_fixed = False
            st.session_state.alert_sent = False
            st.session_state.pop("ollama_message", None)
            st.rerun()

    payload = load_data(demo_mode)
    records = payload["timeseries"]
    incidents = payload["incidents"]
    
    # Send mock alert via Phase 1 logic on initial load
    if not st.session_state.alert_sent:
        service = AlertService()
        for inc in incidents:
            if inc.get("anomaly_score", 0) >= 0.8:
                try:
                    anomaly_model = CostAnomaly(**inc)
                    service.send_alert(anomaly_model)
                except Exception as e:
                    print(f"Pydantic Validation Error: {e}")
        st.session_state.alert_sent = True

    totals = compute_totals(records, fixed=st.session_state.boto_fixed)
    featured = max(incidents, key=lambda item: item["anomaly_score"])

    # Phase 2: Dynamic Consultant Message via Ollama
    spike_impact = sum(r["cost_original"] - r["cost_optimized"] for r in records if r.get("anomaly_score", 0) >= 0.8)
    if st.session_state.boto_fixed:
        explanation = f"Audit update. I've successfully reclaimed {currency(spike_impact)} by running the remediation protocol on {featured['resource']}."
    else:
        if "ollama_message" not in st.session_state:
            with st.spinner("Consulting Llama 3.2..."):
                st.session_state.ollama_message = generate_consultant_insight(featured, spike_impact)
        explanation = st.session_state.ollama_message

    st.markdown(
        f'''
        <div class="hero-card">
          <div style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;flex-wrap:wrap;">
            <div>
              <div class="hero-title">CloudCFO Command Center</div>
              <div class="hero-copy">The automated CFO that handles the "money part" of the cloud.</div>
            </div>
            <div class="hero-copy">Status: {"Fix Deployed" if st.session_state.boto_fixed else "Auditing"}</div>
          </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    top_left, top_mid, top_right = st.columns([1.2, 1.2, 1.4])
    with top_left:
        render_metric_card("Cloud Burn", currency(totals["total_burn"]), f"Optimized floor: {currency(totals['optimized_burn'])}", "30-day modeled AWS spend")
    with top_mid:
        status_sub = "All stable" if totals["anomalies"] == 0 else f"High priority threshold"
        render_metric_card("Anomalies", str(int(totals["anomalies"])), status_sub, f"Count of active waste spikes")
    with top_right:
        render_metric_card("Total Recovery", currency(totals["savings"]), f"Efficiency score: {totals['score']:.1f}%", "Cash reclaimed via scripts")

    main_col, side_col = st.columns([2.25, 1], gap="large")
    with main_col:
        st.markdown('<div class="section-title" style="font-size:1.6rem;">📋 Cloud Checklist</div>', unsafe_allow_html=True)
        bento_left, bento_right = st.columns([1, 1.8], gap="medium")
        with bento_left:
            st.markdown('<div style="color:#0F172A;font-size:1.1rem;line-height:1.6;margin-bottom:2rem;"><b>Issues Found</b><br><span style="color:#64748B;">The engine intercepted a major cost leak. Validate spot pricing structurally before deploying scripts. Review the interactive projections inside the What-If Engine.</span></div>', unsafe_allow_html=True)
            if not st.session_state.boto_fixed:
                st.markdown('''
                <div class="bento-card">
                    <div class="bento-title">A/B Testing for Cost Validation</div>
                    <div class="bento-desc">Simulate architectural changes using real traffic thresholds without disrupting prod environments.</div>
                    <div class="orange-link">Learn more <span>&rarr;</span></div>
                </div>
                ''', unsafe_allow_html=True)

        with bento_right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.plotly_chart(build_cost_figure(records, st.session_state.boto_fixed), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            render_what_if_lab(totals["total_burn"])

    with side_col:
        st.markdown('<div class="section-title">🤖 AI Suite (Consultant)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="star-rating">{"★" * max(1, int(totals["score"]/20))}</div>', unsafe_allow_html=True)
        
        with st.chat_message("assistant"):
            if "typed_out" not in st.session_state:
                # Perform the typewriter effect
                st.markdown('<span style="color:#FF8101;font-weight:700;">Consultant generating...</span>', unsafe_allow_html=True)
                st.write_stream(typewriter_generator(explanation))
                st.session_state.typed_out = True
            else:
                # If already generated this session, just display
                st.write(explanation)

            if not st.session_state.boto_fixed:
                if st.button("Fix Now", type="primary"):
                    anomaly_model = CostAnomaly(**featured)
                    with st.spinner("Invoking Remediator..."):
                        res = fix_resource(anomaly_model, totals["total_burn"], totals["savings"])
                        st.session_state.boto_fixed = True
                        st.session_state.pop("typed_out", None) # Re-trigger typeout
                        st.session_state.pop("ollama_message", None)
                        st.rerun()

        st.caption(f"Asset Map: {featured['resource']} ({featured['service']})")
        
        render_badge(totals["score"])
        
        st.markdown(
            """
            <div class="section-card">
              <div class="section-title">ESG Snapshot</div>
              <div class="mini-grid">
                <div class="mini-card">
                  <div class="mini-label">CO2 Avoided</div>
                  <div class="mini-value">{co2:.0f} kg</div>
                </div>
                <div class="mini-card">
                  <div class="mini-label">Energy Avoided</div>
                  <div class="mini-value">{kwh:.0f} kWh</div>
                </div>
              </div>
            </div>
            """.format(co2=totals["co2_saved"], kwh=totals["savings"] * 10),
            unsafe_allow_html=True,
        )

if __name__ == "__main__":
    main()
