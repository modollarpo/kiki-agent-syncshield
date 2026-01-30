def calculate_roi(ai_revenue, manual_baseline_cost, ai_operating_cost):
    """
    Standard Enterprise ROI Formula:
    ROI = (Net Benefits / Total Costs) * 100
    Net Benefits = (AI Revenue - Manual Baseline Cost) - AI Operating Cost
    """
    net_gain = ai_revenue - manual_baseline_cost
    roi = (net_gain - ai_operating_cost) / ai_operating_cost * 100
    return round(roi, 2)

# Example usage / audit log entry:
if __name__ == "__main__":
    ai_revenue = 50000  # e.g., dollars recovered by SyncEngage + SyncFlow
    manual_cost = 15000 # what it would cost in labor/manual bids
    ai_op_cost = 2000   # compute + API keys
    result = calculate_roi(ai_revenue, manual_cost, ai_op_cost)
    print(f"AI ROI: {result}%")
    # Output: AI ROI: 1650.0%
