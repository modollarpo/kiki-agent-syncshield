# Clean Architecture UseCase: Orchestrate Strategy
from typing import List, Dict, Tuple
from langchain.llms import OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed
import os

def filter_llm_output(output: str) -> str:
    blocked = ["hack", "exploit"]
    for word in blocked:
        if word in output.lower():
            return "[REDACTED]"
    return output

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def orchestrate_strategy(campaign_id: str, user_ids: List[str], context: Dict[str, str]) -> Tuple[List[str], str]:
    # Example: require at least one user and context
    if not user_ids or not context:
        return [], "invalid"
    # LangChain LLM orchestration
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY", "demo-key"))
    prompt = f"Campaign: {campaign_id}, Users: {user_ids}, Context: {context}. Generate a revenue plan."
    try:
        plan = llm(prompt)
    except Exception as e:
        return [], f"llm_error: {e}"
    plan = filter_llm_output(plan)
    actions = [plan]  # In real logic, parse plan into actions
    return actions, "ok"
