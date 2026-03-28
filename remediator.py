import time
from models import CostAnomaly

def fix_resource(resource: CostAnomaly, current_total_burn: float, current_savings: float) -> dict:
    """
    Mock boto3 script that stops a resource and calculates updated savings.
    Returns a dict with the updated metrics.
    """
    time.sleep(1.5) # Simulate API call latency
    
    # Calculate impact (the simulated waste being stopped)
    impact = resource.cost_usd * 0.85
    
    new_burn = max(current_total_burn - impact, 0)
    new_savings = current_savings + impact
    
    return {
        "status": "success",
        "message": f"Successfully stopped {resource.resource_id} on {resource.service}.",
        "new_burn": new_burn,
        "new_savings": new_savings
    }
