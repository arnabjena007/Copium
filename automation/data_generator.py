import json
import random
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "mock_data.json"

def generate_enterprise_data():
    today = datetime.now()
    dates = [(today - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(30, 0, -1)]
    
    timeseries = []
    
    # Establish a baseline of ~$8,500 / day
    for i, date_str in enumerate(dates):
        # Normal daily variance +/- 10%
        base_cost = random.randint(8000, 9000)
        optimized = int(base_cost * 0.85)
        
        # Introduce distinct massive anomalies on different days
        if i == 12:
            cost = base_cost + 8500
            timeseries.append({
                "date": date_str,
                "cost_original": cost,
                "cost_optimized": optimized,
                "anomaly_score": 0.89,
                "wasted_cost": cost - optimized,
                "service": "RDS",
                "resource": "prod-analytics-db",
                "owner": "Data",
                "reason": "IOPS provisioned way beyond actual usage requirement"
            })
        elif i == 19:
            cost = base_cost + 11200
            timeseries.append({
                "date": date_str,
                "cost_original": cost,
                "cost_optimized": optimized,
                "anomaly_score": 0.94,
                "wasted_cost": cost - optimized,
                "service": "EC2",
                "resource": "spark-worker-fleet",
                "owner": "DataEngineering",
                "reason": "on-demand instances used instead of spot for massive batch job"
            })
        elif i == 25:
            cost = base_cost + 14500
            timeseries.append({
                "date": date_str,
                "cost_original": cost,
                "cost_optimized": optimized,
                "anomaly_score": 0.98,
                "wasted_cost": cost - optimized,
                "service": "SageMaker",
                "resource": "train-job-x99-xlarge",
                "owner": "DataScience",
                "reason": "runaway hyperparameter tuning job left running over the weekend"
            })
        else:
            anomaly = random.uniform(0.1, 0.4) # Below 0.8 threshold
            timeseries.append({
                "date": date_str,
                "cost_original": base_cost,
                "cost_optimized": optimized,
                "anomaly_score": anomaly,
                "wasted_cost": base_cost - optimized,
                "service": random.choice(["EC2", "RDS", "EKS", "S3", "ElastiCache", "Kafka"]),
                "resource": f"cluster-node-{random.randint(10,99)}",
                "owner": random.choice(["Platform", "Core", "Data", "Security"]),
                "reason": "general resource bloat"
            })
            
    # The incident array only tracks the high-threat anomalies (>= 0.8)
    spikes = [t for t in timeseries if t["anomaly_score"] >= 0.8]
    incidents = []
    for s in spikes:
        incidents.append({
            "service": s["service"],
            "resource": s["resource"],
            "owner": s["owner"],
            "anomaly_score": s["anomaly_score"],
            "cost_original": s["cost_original"],
            "cost_optimized": s["cost_optimized"],
            "reason": s["reason"]
        })
        
    # We output "baseline" and "demo" as the exact same payload
    # so the frontend works flawlessly without strict mode checking
    payload = {
        "baseline": {
            "timeseries": timeseries,
            "incidents": incidents
        },
        "demo": {
            "timeseries": timeseries,
            "incidents": incidents
        }
    }
    
    # Ensure dir exists
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        
    print(f"Generated 30 days of Enterprise AWS data with {len(incidents)} severe anomalies.")
    print(f"File written to: {DATA_PATH.relative_to(ROOT)}")

if __name__ == "__main__":
    generate_enterprise_data()
