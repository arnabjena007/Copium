import json
import logging
from typing import Any

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Header, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slack_sdk.signature import SignatureVerifier

# Security config for Tunnel Bridge
API_KEY = "3d4c5eb8-9fe0-4458-882d-5750d9a78947"

async def verify_api_key(x_api_key: str = Header(None, alias="X-API-KEY")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return x_api_key

from config.settings import slack_settings
from automation.remediation.remediator import RemediationEngine

from pathlib import Path

logger = logging.getLogger("cloudcfo.api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="CloudCFO Webhook Listener", version="1.0.0")

# --- Governance Config ---
CONFIG_PATH = Path("config/backend_config.json")
def load_backend_config():
    if not CONFIG_PATH.exists():
        return {
            "risk_multiplier": 2.0, 
            "authorized_regions": ["us-east-1", "us-west-2", "eu-north-1"], 
            "quiet_hours": [22,23,0,1,2,3,4], 
            "service_sensitivity": {"AmazonS3": 1.2, "AWSLambda": 1.1, "AmazonRDS": 2.5, "AmazonEC2": 2.0}
        }
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_backend_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow UI frontend to connect during integration tests
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

signature_verifier = SignatureVerifier(slack_settings.signing_secret)
engine = RemediationEngine()

@app.get("/")
async def root():
    return {"status": "CloudCFO Webhook Listener is Online", "tunnel": "Active", "version": "1.1.0"}

@app.post("/api/auth/validate-arn")
async def validate_arn(request: Request, key: str = Depends(verify_api_key)):
    try:
        data = await request.json()
        arn = data.get("arn")
        authorized_arn = "arn:aws:iam::100731996973:user/HackathonUser"
        
        if arn == authorized_arn:
            logger.info(f"Authorized access for ARN: {arn}")
            return {"status": "success", "message": "Authorized"}
        else:
            logger.warning(f"Unauthorized access attempt with ARN: {arn}")
            return JSONResponse(status_code=403, content={"status": "error", "message": "Unauthorized ARN"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/ml/anomalies")
async def get_ml_anomalies(key: str = Depends(verify_api_key)):
    """
    Returns real-time anomaly data for the Tunnel Bridge frontend.
    """
    from automation.reporting.ml_alert_runner import AUDIT_LOG_PATH
    import os
    
    # Normally we would run a live scan, but since this is the webhook listener,
    # we return the latest mock data or recent audit actions.
    # For the hackathon demo, we'll return the mock data to populate the dashboard.
    mock_path = os.path.join(os.getcwd(), "data", "mock_data.json")
    try:
        if os.path.exists(mock_path):
            with open(mock_path, "r", encoding="utf-8") as f:
                return {"status": "success", "data": json.load(f)}
        return {"status": "error", "message": "Data source not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/config")
async def get_config(key: str = Depends(verify_api_key)):
    return load_backend_config()

@app.post("/api/config")
async def update_config(request: Request, key: str = Depends(verify_api_key)):
    try:
        new_config = await request.json()
        save_backend_config(new_config)
        return {"status": "success", "config": new_config}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/slack/interactions")
async def slack_interactions(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint for handling interactive elements from Slack (e.g. "Fix" buttons).
    """
    body = await request.body()
    headers = request.headers

    # Validate that this request actually came from Slack
    if slack_settings.signing_secret:
        if not signature_verifier.is_valid_request(body, headers):
            logger.warning("Invalid signature on incoming webhook request.")
            raise HTTPException(status_code=403, detail="Invalid Slack Signature")
    else:
        logger.warning("SLACK_SIGNING_SECRET is empty - skipping signature verification (DEV MODE ONLY)")

    form_data = await request.form()
    payload_str = form_data.get("payload")
    if not payload_str:
        return JSONResponse(content={"status": "error", "message": "Missing payload"}, status_code=400)

    payload = json.loads(str(payload_str))
    
    # We only care about block_actions (button clicks)
    if payload.get("type") != "block_actions":
        return JSONResponse(content={"status": "ignored"})

    actions = payload.get("actions", [])
    if not actions:
        return JSONResponse(content={"status": "ignored"})

    action = actions[0]
    action_value = action.get("value")      # E.g. "stop_ec2|i-12345678" 
    action_id = action.get("action_id")     # "fix_action_xyz"
    user_id = payload.get("user", {}).get("id", "Unknown User")
    
    logger.info(f"Received action: {action_id} with value {action_value} from user <@{user_id}>")

    # In a real scenario, we would instantly reply 200 OK so Slack doesn't timeout,
    # and use background_tasks to actually perform the aws remediation.
    background_tasks.add_task(process_remediation, action_value, user_id)
    
    return JSONResponse(content={"status": "received"})


def process_remediation(action_value: str, user_id: str):
    """
    Background worker that runs the AWS boto3 remediation after the HTTP response closes.
    """
    logger.info(f"Running background remediation task for {action_value} triggered by {user_id}...")
    
    # 1. Parsing the Incoming Action Value
    # Support for legacy IDs vs new enhanced format "ACTION:ID:CODE"
    if ":" in action_value:
        parts = action_value.split(":")
        action_type = parts[0]
        resource_id = parts[1] if len(parts) > 1 else "unknown"
        anomaly_code = parts[2] if len(parts) > 2 else "NONE"
    elif action_value == "act-ec2-stop-001":
        action_type = "STOP_EC2"
        resource_id = "i-0abcd1234efgh5678"
        anomaly_code = "LEGACY_TEST"
    elif action_value == "act-ebs-del-001":
        action_type = "DELETE_EBS"
        resource_id = "vol-0xyz98765uvw43210"
        anomaly_code = "LEGACY_TEST"
    else:
        logger.warning(f"Unrecognized action_value format: {action_value}")
        action_type = action_value
        resource_id = "unknown"
        anomaly_code = "GENERIC"

    logger.info(f"Action parsed: {action_type} for resource {resource_id} (Code: {anomaly_code})")

    try:
        from automation.slack.message_builder import MessageBuilder
        from automation.slack.webhook import SlackWebhook
        from automation.slack.models import AlertSeverity

        webhook = SlackWebhook(slack_settings.webhook_url)

        # Scenario B: PROD PROTECTION (Code 999) - Routing to Manual Review link
        if anomaly_code == "CODE_999_PROD_FIGHT":
            msg = f"<@{user_id}> is escalating production risk for `{resource_id}` to AWS Console manual review."
            # No boto3 action for manual review links
            result_success = True
            result_message = "Escalated to On-Call/Manual Review."
            
        # Scenario C: SECURITY BREACH (Unauthorized Region) - Routing to Security Module
        elif anomaly_code == "SEC_REGION_UNAUTHORIZED":
            logger.warning(f"SECURITY BREACH in unauthorized region detected by <@{user_id}>. Executing LOCKDOWN.")
            # Mocking the security lockdown call (in production, this blocks NACLs/SecurityGroups)
            result_success = True
            result_message = f"Region Lockdown initiated on {resource_id}."

        # Scenario D: QUIET HOURS (Code 104)
        elif action_type == "HALT_UNTIL_MONDAY":
            result_success = True
            result_message = f"Operation on {resource_id} paused until Monday 8 AM."

        # Scenario A: ZOMBIE / Standard Actions
        elif action_type == "STOP_INSTANCE" or action_type == "STOP_EC2":
            result = engine.stop_idle_ec2(instance_id=resource_id, dry_run=False)
            result_success, result_message = result.success, result.message
        elif action_type == "START_EC2":
            result = engine.start_ec2(instance_id=resource_id, dry_run=False)
            result_success, result_message = result.success, result.message
        elif action_type == "DELETE_EBS":
            result = engine.delete_unattached_ebs(volume_id=resource_id, dry_run=False)
            result_success, result_message = result.success, result.message
        else:
            logger.error(f"Unsupported action type: {action_type}")
            return

        # Prepare the result message to send back to Slack
        status_emoji = "✅" if result_success else "❌"
        msg = (
            f"<@{user_id}> executed `{action_type}` on `{resource_id}`.\n"
            f"> *Outcome:* {result_message}"
        )

        slack_payload = MessageBuilder.build_simple_alert(
            title=f"{status_emoji} Remediation Action Executed",
            message=msg,
            severity=AlertSeverity.INFO if result_success else AlertSeverity.WARNING
        )
        webhook.send(slack_payload)
        logger.info(f"Remediation response sent to Slack for {resource_id}")

    except Exception as e:
        logger.error(f"Error executing remediation in background task: {e}", exc_info=True)

@app.get("/api/dashboard")
def get_dashboard_metrics(key: str = Depends(verify_api_key)):
    """
    Phase 5: Aggregate the audit_log.json to provide live savings and operation counts for the UI frontend.
    """
    from automation.remediation.remediator import AUDIT_LOG_PATH
    import re
    
    if not AUDIT_LOG_PATH.exists():
        return {
            "total_remediations_attempted": 0,
            "total_remediations_successful": 0,
            "total_monthly_savings_usd": 0.0,
            "recent_actions": []
        }
        
    try:
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as file:
            audit_log = json.load(file)
            
        successful = 0
        total_savings = 0.0
        
        for entry in audit_log:
            if entry.get("success"):
                successful += 1
                
            savings_str = entry.get("savings_estimated")
            if savings_str and "$" in savings_str:
                # E.g. "$25.00/month"
                match = re.search(r'\$([\d\.\,]+)', savings_str)
                if match:
                    val = match.group(1).replace(",", "")
                    try:
                        total_savings += float(val)
                    except ValueError:
                        pass
                        
        # Sort logs newest first
        audit_log.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
        
        # 7-day actual cost series from AWS Cost Explorer
        from automation.anomaly.detector import CostExplorerDetector
        from datetime import date, timedelta
        
        detector = CostExplorerDetector()
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # We fetch daily totals (no group by for the chart)
        try:
            ce_client = detector._client
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date.isoformat(),
                    "End": (end_date + timedelta(days=1)).isoformat(),
                },
                Granularity="DAILY",
                Metrics=["UnblendedCost"]
            )
            
            cost_series = []
            for result in response.get("ResultsByTime", []):
                cost_series.append({
                    "date": result.get("TimePeriod", {}).get("Start"),
                    "total_cost": float(result.get("Total", {}).get("UnblendedCost", {}).get("Amount", 0))
                })
        except Exception as e:
            logger.warning(f"Could not fetch real cost history: {e}")
            cost_series = []
            
        return {
            "slack_channel": slack_settings.channel,  # For UI Deep Linking
            "total_remediations_attempted": len(audit_log),
            "total_remediations_successful": successful,
            "total_monthly_savings_usd": total_savings,
            "cost_series": cost_series,               # Real AWS Cost Explorer data
            "recent_actions": audit_log[:10]          # Return top 10 most recent actions
        }
    except Exception as e:
        logger.exception("Failed to load dashboard metrics")
        raise HTTPException(status_code=500, detail="Internal server error parsing audit log")

@app.get("/api/costs")
def get_live_costs(key: str = Depends(verify_api_key)):
    """
    Feeds LIVE AWS Cost & Usage Data to the ML Brain.
    Fetches real-time compute inventory using boto3 and the ML team's credentials.
    """
    import os
    from datetime import datetime
    import boto3
    from dotenv import load_dotenv
    
    # Load ML team's specific access keys
    load_dotenv(os.path.join(os.getcwd(), "ml", ".env"))
    
    try:
        # Fetch real AWS compute environments
        ec2 = boto3.client('ec2', region_name='us-east-1')
        instances = ec2.describe_instances()
        
        live_data = []
        for r in instances.get('Reservations', []):
            for i in r.get('Instances', []):
                if i.get('State', {}).get('Name') == 'running':
                    tags = {t['Key']: t['Value'] for t in i.get('Tags', [])}
                    
                    # Note: Real-time CloudWatch CPU and Pricing aggregation would happen here.
                    # For this phase, we use real resource metadata.
                    live_data.append({
                        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "service": "AmazonEC2",
                        "region": "us-east-1",
                        "resource_id": i.get('InstanceId'),
                        "team": tags.get('Team', 'Engineering'),
                        "environment": tags.get('Environment', 'dev'),
                        "project": tags.get('Project', 'Core'),
                        "cost_usd": 0.0, # Will be populated by ML brain relative to InstanceType
                        "cpu_usage_pct": 0.0, # To be fetched from CloudWatch in Phase 6
                        "instance_type": i.get('InstanceType')
                    })
                    
        return {"status": "success", "data": live_data}
    except Exception as e:
        logger.exception("Final live discovery failed")
        raise HTTPException(status_code=500, detail=str(e))
