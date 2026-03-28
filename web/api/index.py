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
    return {
        "total_remediations_attempted": 25,
        "total_remediations_successful": 24,
        "total_monthly_savings_usd": 1250.00,
        "recent_actions": [
            {
                "timestamp": "2026-03-28T10:58:12Z",
                "action": "STOP_EC2",
                "resource_id": "i-0abcd1234efgh5678",
                "mode": "LIVE",
                "success": True,
                "message": "Stop requested successfully.",
                "insight": "Mistral AI detected zero CPU utilization over 72h. Terminating this idle instance saved $450/mo with no impact on production workloads."
            },
            {
                "timestamp": "2026-03-28T10:45:00Z",
                "action": "DELETE_EBS",
                "resource_id": "vol-0987654321fedcba",
                "mode": "LIVE",
                "success": True,
                "message": "Volume deleted.",
                "insight": "Unattached volume found in us-east-1. Deletion prevents 'zombie' costs that account for 12% of your monthly storage waste."
            },
            {
                "timestamp": "2026-03-28T10:30:15Z",
                "action": "RIGHTSIZE_RDS",
                "resource_id": "db-prod-instance",
                "mode": "DRY_RUN",
                "success": False,
                "message": "Dry-run check: No changes made.",
                "insight": "RDS instance is over-provisioned by 4x. Recommend downgrading from db.r5.2xlarge to db.m5.large for a $800/mo cost reduction."
            }
        ]
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "engine": "Vercel Serverless"}
