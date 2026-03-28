import json
from models import CostAnomaly, IdleResource
from typing import Union

class AlertService:
    def __init__(self):
        self.webhook_url = "mock_slack_webhook"
        self.color_palette = {
            "critical": "#FB7185", # Aura Red
            "warning": "#FACC15",  # Aura Gold
            "good": "#5EEAD4"      # Aura Teal
        }
    
    def send_alert(self, payload: Union[CostAnomaly, IdleResource]):
        is_anomaly = isinstance(payload, CostAnomaly)
        color = self.color_palette["critical"] if is_anomaly and getattr(payload, "is_anomaly", False) else self.color_palette["warning"]
        
        message = {
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 Cloud Cost Alert: {payload.service}",
                    "text": f"Owner: {getattr(payload, 'team', 'Unknown')}\nResource: {getattr(payload, 'resource_id', 'Unknown')}",
                    "fields": [
                        {
                            "title": "Cost Impact",
                            "value": f"${payload.cost_usd if hasattr(payload, 'cost_usd') else getattr(payload, 'wasted_cost', 0):.2f}",
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        print(f"[AlertService] Mock Slack Alert Sent:")
        print(json.dumps(message, indent=2))
        return message
