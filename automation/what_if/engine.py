class WhatIfEngine:
    def __init__(self):
        # Sample AWS Price Multipliers (Normalized to On-Demand = 1.0)
        self.market_rates = {
            "spot_discount": 0.70,  # Spot is roughly 70% cheaper
            "reserved_discount": 0.40, # RI is roughly 40% cheaper
            "mumbai_premium": 0.90, # Assume Mumbai is 10% cheaper than US-East-1 for demo
            "ireland_premium": 1.15  # Assume Ireland is 15% more expensive
        }

    def simulate_spot_migration(self, current_monthly_spend: float):
        projected = current_monthly_spend * (1 - self.market_rates["spot_discount"])
        savings = current_monthly_spend - projected
        return {"current": current_monthly_spend, "projected": projected, "savings": savings}

    def simulate_regional_migration(self, current_monthly_spend: float, target_region: str):
        multiplier = self.market_rates.get(f"{target_region.lower()}_premium", 1.0)
        projected = current_monthly_spend * multiplier
        savings = current_monthly_spend - projected
        return {"current": current_monthly_spend, "projected": projected, "savings": savings}
