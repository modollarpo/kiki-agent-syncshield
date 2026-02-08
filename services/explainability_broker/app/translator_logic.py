from enum import Enumfrom enum import Enum










































    }        'timestamp': metadata.get('timestamp'),        'action': action_type,        'agent': agent_id,        'severity': severity,        'narrative': narrative,    return {        narrative = template.replace('{details}', str(metadata))    except Exception:        narrative = template.format(**metadata)    try:    template, severity = TEMPLATES.get(key, ("KIKI performed an action: {details}", SeverityLevel.INSIGHT))    key = (agent_id, action_type)def translate_log(agent_id: str, action_type: str, metadata: Dict[str, Any]) -> Dict[str, Any]:}    ),        SeverityLevel.OPTIMIZATION        "SyncBrain shifted ${amount} from {from_platform} to {to_platform} because the cost-per-acquisition is currently {cpa_delta}% lower on {to_platform}.",    ('SyncBrain', 'pivot'): (    ),        SeverityLevel.INSIGHT        "SyncTwin just verified a new strategy for next week. We predict a {revenue_lift}% revenue lift with {confidence}% confidence.",    ('SyncTwin', 'simulation'): (    ),        SeverityLevel.GUARDIAN        "KIKI automatically paused Ad Variation #{creative_id}. It was underperforming compared to your historical baseline, saving you ${savings} in wasted spend today.",    ('SyncShield', 'rollback'): (    ),        SeverityLevel.OPTIMIZATION        "KIKI increased your {platform} bid by {percent}% because it detected a cluster of high-LTV users currently active.",    ('SyncFlow', 'bid_increase'): (TEMPLATES = {# Reasoning templates for each agent/action    INSIGHT = 'Insight'    GUARDIAN = 'Guardian'    OPTIMIZATION = 'Optimization'class SeverityLevel(str, Enum):from typing import Dict, Anyfrom typing import Dict, Any

class Severity(str, Enum):
    OPTIMIZATION = 'Optimization'
    GUARDIAN = 'Guardian'
    INSIGHT = 'Insight'

# Template map: (AgentID, ActionType) -> (template, severity)
TEMPLATES = {
    ('SyncFlow', 'bid_increase'): (
        "KIKI increased your {platform} bid by {percent}% because it detected a cluster of high-LTV users currently active.",
        Severity.OPTIMIZATION),
    ('SyncShield', 'rollback'): (
        "KIKI automatically paused {asset}. It was underperforming compared to your historical baseline, saving you ${savings} in wasted spend today.",
        Severity.GUARDIAN),
    ('SyncTwin', 'simulation'): (
        "SyncTwin just verified a new strategy for next week. We predict a {revenue_lift}% revenue lift with {confidence}% confidence.",
        Severity.INSIGHT),
    ('SyncBrain', 'pivot'): (
        "SyncBrain shifted ${amount} from {from_platform} to {to_platform} because the cost-per-acquisition is currently {cpa_delta}% lower on {to_platform}.",
        Severity.OPTIMIZATION),
}

def explainability_translate(log: Dict[str, Any]) -> Dict[str, Any]:
    agent = log.get('agent')
    action = log.get('action')
    meta = log.get('meta', {})
    key = (agent, action)
    if key in TEMPLATES:
        template, severity = TEMPLATES[key]
        try:
            narrative = template.format(**meta)
        except Exception:
            narrative = f"{agent} performed {action}."
    else:
        narrative = f"{agent} performed {action}."
        severity = Severity.INSIGHT
    return {
        'time': log.get('time'),
        'message': narrative,
        'severity': severity,
        'agent': agent,
        'raw': log
    }
