from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/dashboard/ai-vs-manual-kpis")
def get_ai_vs_manual_kpis():
    """
    Returns the AI vs. Manual Performance KPIs for the dashboard table.
    """
    data = [
        {
            "metric": "Execution Speed",
            "ai_agent": "< 1ms (SyncFlow)",
            "manual_baseline": "5–10 Minutes",
            "revenue_win": "99.9% faster response to market shifts."
        },
        {
            "metric": "Creative Yield",
            "ai_agent": "100+ variants/hr (SyncCreate)",
            "manual_baseline": "1–2 variants/day",
            "revenue_win": "50x more testing for high-LTV users."
        },
        {
            "metric": "Cost Per Lead",
            "ai_agent": "Dynamic Bidding (SyncReflex)",
            "manual_baseline": "Fixed/Rule-based",
            "revenue_win": "~30% reduction in wasted ad spend."
        },
        {
            "metric": "Retention (LTV)",
            "ai_agent": "Predictive Win-backs (SyncEngage)",
            "manual_baseline": "Reactive/Manual",
            "revenue_win": "~15% increase in recovered customer value."
        }
    ]
    return JSONResponse(content={"kpis": data})
