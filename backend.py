import os
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).parent / "data" / "mock_data.json"

@app.get("/metrics/latest")
def get_latest_metrics():
    try:
        with DATA_PATH.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return {"baseline": payload["baseline"], "status": "active"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/dashboard")
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
                "success": true,
                "message": "Stop requested successfully."
            },
            {
                "timestamp": "2026-03-28T10:45:00Z",
                "action": "DELETE_EBS",
                "resource_id": "vol-0987654321fedcba",
                "mode": "LIVE",
                "success": true,
                "message": "Volume deleted."
            },
            {
                "timestamp": "2026-03-28T10:30:15Z",
                "action": "RIGHTSIZE_RDS",
                "resource_id": "db-prod-instance",
                "mode": "DRY_RUN",
                "success": false,
                "message": "Dry-run check: No changes made."
            }
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
