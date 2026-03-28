import os
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import Any, Dict

app = FastAPI()

# Enable CORS for local development (Vercel will ignore this in same-domain deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In Vercel, the file is in web/api/index.py, and data is in web/data/mock_data.json
DATA_PATH = Path(__file__).parent.parent / "data" / "mock_data.json"

@app.get("/metrics/latest")
def get_latest_metrics():
    try:
        if not DATA_PATH.exists():
            return {"error": f"Data not found at {DATA_PATH}", "status": "offline"}
        with DATA_PATH.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return {"baseline": payload["baseline"], "status": "active"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/dashboard")
def get_dashboard_data():
    import time
    import random
    
    # Base numbers
    base_attempted = 25
    base_successful = 24
    base_savings = 1250.00
    
    # Current time in minutes to determine "session progress"
    # This ensures everyone sees new events appearing over time
    current_min = int(time.time() / 60)
    # We add 1 new event every 2 minutes or so for the demo
    extra_events_count = (current_min % 60) // 2
    
    # Calculate updated KPIs
    attempted = base_attempted + extra_events_count
    successful = base_successful + extra_events_count
    savings = base_savings + (extra_events_count * 15.5) # Average saving per action
    
    # Static historical actions
    actions = [
        {
            "timestamp": "2026-03-28T10:58:12Z",
            "action": "STOP_EC2",
            "resource_id": "i-0abcd1234efgh5678",
            "mode": "LIVE",
            "success": True,
            "message": "Stop requested successfully.",
            "insight": "Mistral AI detected zero CPU utilization over 72h. Terminating this idle instance saved $450/mo with no impact on production workloads.",
            "origin": "slack"
        },
        {
            "timestamp": "2026-03-28T10:45:00Z",
            "action": "DELETE_EBS",
            "resource_id": "vol-0987654321fedcba",
            "mode": "LIVE",
            "success": True,
            "message": "Volume deleted.",
            "insight": "Unattached volume found in us-east-1. Deletion prevents 'zombie' costs that account for 12% of your monthly storage waste.",
            "origin": "slack"
        },
        {
            "timestamp": "2026-03-28T10:30:15Z",
            "action": "RIGHTSIZE_RDS",
            "resource_id": "db-prod-instance",
            "mode": "DRY_RUN",
            "success": False,
            "message": "Dry-run check: No changes made.",
            "insight": "RDS instance is over-provisioned by 4x. Recommend downgrading from db.r5.2xlarge to db.m5.large for a $800/mo cost reduction.",
            "origin": "system"
        }
    ]
    
    # Add "New" dynamic events from Slack if enough time has passed
    if extra_events_count > 0:
        for i in range(1, extra_events_count + 1):
            # Create a "fresh" event
            # Use current time minus some offset for the dynamic actions
            event_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - (i * 120)))
            actions.insert(0, {
                "timestamp": event_time,
                "action": random.choice(["STOP_EC2", "TERMINATE_IDLE", "CLEAN_SNAPSHOTS"]),
                "resource_id": f"res-{random.randint(1000, 9999)}-dynamic",
                "mode": "LIVE",
                "success": True,
                "message": "Automated remediation triggered via Slack approval.",
                "insight": f"Live Update: This cost-saving action was approved by an administrator in #finops-alerts via the Mistral AI bot. Estimated impact: ${random.randint(20, 150)}/mo.",
                "origin": "slack"
            })

    return {
        "total_remediations_attempted": attempted,
        "total_remediations_successful": successful,
        "total_monthly_savings_usd": round(savings, 2),
        "recent_actions": actions[:10] # Keep feed clean
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "engine": "Vercel Serverless"}
