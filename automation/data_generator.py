import json
import random
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "mock_data.json"

def generate_enterprise_data():
    today = datetime.now()
    dates = [(today - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(30, 0, -1)]
    
    # Pass 1: Generate Raw Data without hardcoded ML scores
    raw_data = []
    
    for i, date_str in enumerate(dates):
        # Normal daily variance +/- 10%
        base_cost = random.randint(8000, 9000)
        optimized = int(base_cost * 0.85)
        
        # Introduce distinct massive anomalies on different days
        if i == 12:
            cost = base_cost + 8500
            raw_data.append({
                "date": date_str, "cost_original": cost, "cost_optimized": optimized, "wasted_cost": cost - optimized,
                "service": "RDS", "resource": "prod-analytics-db", "owner": "Data", "reason": "IOPS provisioned way beyond actual usage requirement"
            })
        elif i == 19:
            cost = base_cost + 11200
            raw_data.append({
                "date": date_str, "cost_original": cost, "cost_optimized": optimized, "wasted_cost": cost - optimized,
                "service": "EC2", "resource": "spark-worker-fleet", "owner": "DataEngineering", "reason": "on-demand instances used instead of spot for massive batch job"
            })
        elif i == 25:
            cost = base_cost + 14500
            raw_data.append({
                "date": date_str, "cost_original": cost, "cost_optimized": optimized, "wasted_cost": cost - optimized,
                "service": "SageMaker", "resource": "train-job-x99-xlarge", "owner": "DataScience", "reason": "runaway hyperparameter tuning job left running over the weekend"
            })
        else:
            raw_data.append({
                "date": date_str, "cost_original": base_cost, "cost_optimized": optimized, "wasted_cost": base_cost - optimized,
                "service": random.choice(["EC2", "RDS", "EKS", "S3", "ElastiCache", "Kafka"]),
                "resource": f"cluster-node-{random.randint(10,99)}", "owner": random.choice(["Platform", "Core", "Data", "Security"]),
                "reason": "general resource bloat"
            })

    # Pass 2: Isolation Forest Machine Learning
    X = np.array([r["cost_original"] for r in raw_data]).reshape(-1, 1)
    
    # contamination=0.1 means we expect roughly 10% of our 30 days (3 days) to be anomalies
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)
    
    # In sklearn, decision_function returns < 0 for outliers. 
    # The more negative, the more anomalous. Let's invert it so higher = more anomalous.
    raw_scores = -model.decision_function(X)
    
    # Normalize scores between 0.1 and 1.0 for the UI
    min_val, max_val = raw_scores.min(), raw_scores.max()
    normalized_scores = 0.1 + 0.9 * ((raw_scores - min_val) / (max_val - min_val))
    
    # Pass 3: Map ML scores back into the objects
    timeseries = []
    incidents = []
    
    for i, data in enumerate(raw_data):
        score = float(normalized_scores[i])
        data["anomaly_score"] = round(score, 3)
        timeseries.append(data)
        
        # If the ML score is strongly anomalous (e.g. >= 0.8), it's a confirmed incident
        if score >= 0.8:
            incidents.append(data)
            
    payload = {
        "baseline": { "timeseries": timeseries, "incidents": incidents },
        "demo": { "timeseries": timeseries, "incidents": incidents }
    }
    
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        
    print(f"Generated AWS data with {len(incidents)} mathematically confirmed model anomalies.")
    print(f"File written to: {DATA_PATH.relative_to(ROOT)}")

if __name__ == "__main__":
    generate_enterprise_data()
