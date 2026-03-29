import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from sklearn.ensemble import IsolationForest

class CloudMLBrain:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default to look in same directory as this file
            config_path = str(Path(__file__).parent / "config.json")
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                self.config = json.load(file)
        else:
            self.config = {
                "risk_multiplier": 2.0,
                "authorized_regions": ["us-east-1", "us-west-2", "eu-north-1"],
                "quiet_hours": [22, 23, 0, 1, 2, 3, 4],
                "service_sensitivity": {}
            }
        
        self.risk_multiplier = self.config.get("risk_multiplier", 2.0)
        self.auth_regions = self.config.get("authorized_regions", [])
        self.quiet_hours = self.config.get("quiet_hours", [])
        self.service_sens = self.config.get("service_sensitivity", {})

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processes a dataframe of resource records and returns enriched intelligence."""
        if df.empty:
            return df
        
        # 1. Clean NaNs & Feature Engineering
        if 'cpu_usage_pct' not in df.columns:
            df['cpu_usage_pct'] = 0.0
        
        df['cpu_usage_pct'] = pd.to_numeric(df['cpu_usage_pct'], errors='coerce').fillna(0)
        # The "Zombie Hunter" Metric
        df['cost_per_cpu'] = df['cost_usd'] / (df['cpu_usage_pct'] + 0.1)

        # 2. Train Isolation Forest
        features = ['cost_usd', 'cpu_usage_pct', 'cost_per_cpu']
        # Safety: handle all-zero or single-record dataframes for mock scenarios
        if len(df) > 1:
            model = IsolationForest(contamination=0.01, random_state=42)
            df['raw_prediction'] = model.fit_predict(df[features])
            df['is_anomaly'] = df['raw_prediction'].map({1: False, -1: True})
            df['anomaly_score_raw'] = model.decision_function(df[features])
        else:
            df['is_anomaly'] = False
            df['anomaly_score_raw'] = 0.0

        # 3. Hybrid Severity Scoring & Guardrails
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        
        # Dynamic baseline calculation
        df['hourly_service_avg'] = df.groupby(['service', 'hour'])['cost_usd'].transform('mean')
        critical_threshold = np.percentile(df['anomaly_score_raw'], 0.1) if len(df) > 1 else -1.0

        def apply_guardrails(row):
            severity = "NORMAL"
            reason_code = "CODE_200_NORMAL"
            action = "NONE"
            
            # Guardrail 1: Geofencing
            if row['region'] not in self.auth_regions:
                return pd.Series(["CRITICAL", "SEC_REGION_UNAUTHORIZED", "BLOCK_REGION_ACCESS"])

            # Guardrail 2: Environment Hierarchy
            is_prod = True if str(row['environment']).lower() in ['prod', 'production'] else False
            
            # Guardrail 3: Service-Relative Thresholding
            dynamic_multiplier = self.service_sens.get(row['service'], self.risk_multiplier)
            is_price_spike = row['cost_usd'] > (row['hourly_service_avg'] * dynamic_multiplier)

            # Guardrail 4: Quiet Hours
            is_quiet_hour = True if row['hour'] in self.quiet_hours else False
            
            if row['is_anomaly'] or is_price_spike:
                severity = "WARNING"
                reason_code = "CODE_103_SPEND_SPIKE"
                action = "INVESTIGATE"
                
                if is_prod:
                    severity = "CRITICAL"
                    reason_code = "CODE_999_PROD_FIGHT"
                    action = "MANUAL_REVIEW_REQUIRED" 
                elif row['cpu_usage_pct'] < 5:
                    severity = "CRITICAL"
                    reason_code = "CODE_101_ZOMBIE"
                    action = "STOP_INSTANCE"
                elif is_quiet_hour:
                    severity = "CRITICAL"
                    reason_code = "CODE_104_OFF_HOURS_ACTIVITY"
                    action = "HALT_UNTIL_MONDAY"

            if severity == "NORMAL" and row['anomaly_score_raw'] <= critical_threshold and len(df) > 1:
                severity = "WARNING"
                reason_code = "CODE_105_ML_OUTLIER"
                action = "INVESTIGATE"

            return pd.Series([severity, reason_code, action])

        df[['severity', 'anomaly_code', 'suggested_action']] = df.apply(apply_guardrails, axis=1)
        
        return df

if __name__ == "__main__":
    # Regression test for script mode
    brain = CloudMLBrain()
    print("🧠 ML Brain class initialized. Running regression test...")
    # Mock some data if API is not accessible
    try:
        df_test = pd.DataFrame([{
            "timestamp": "2026-03-28 12:00:00", "service": "AmazonEC2", "region": "us-east-1",
            "resource_id": "i-test", "cost_usd": 150.0, "cpu_usage_pct": 2.1,
            "environment": "Production", "team": "DevOps", "project": "Test"
        }])
        enriched = brain.analyze(df_test)
        print(f"✅ Regression Successful. Detected severity: {enriched['severity'].iloc[0]}")
    except Exception as e:
        print(f"❌ Regression Failed: {e}")