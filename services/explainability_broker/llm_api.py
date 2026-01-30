import openai
import os
from typing import Dict

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_business_narrative(event: Dict) -> str:
    prompt = f"""
You are KIKI, an AI revenue strategist. Given the following event metadata, generate a concise, client-facing business narrative that explains the 'Why', 'What', and 'So What' of the action:

Event: {event}

Format:
Why: <reason/observation>
What: <action>
So What: <outcome/ROI>
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a business analyst."},
                  {"role": "user", "content": prompt}],
        max_tokens=120
    )
    return response.choices[0].message['content'].strip()

def generate_technical_audit(event: Dict) -> str:
    prompt = f"""
You are KIKI, an AI system auditor. Given the following event metadata, generate a technical audit log entry for an admin:

Event: {event}

Format:
Agent: <agent>
Reason: <reasoning/threshold>
Action: <action>
Recovery: <recovery_path>
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a system auditor."},
                  {"role": "user", "content": prompt}],
        max_tokens=120
    )
    return response.choices[0].message['content'].strip()
