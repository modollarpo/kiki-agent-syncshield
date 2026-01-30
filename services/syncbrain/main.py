


from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import grpc
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../shared/types/python')))
import kiki_core_pb2_grpc
import kiki_core_pb2
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


app = FastAPI(title="KIKI SyncBrain")
Instrumentator().instrument(app).expose(app)

@app.post("/plan")
async def coordinate_strategy(user_id: str, data: list):
    # 1. Call SyncValue via gRPC (async)
    async with grpc.aio.insecure_channel('syncvalue:50051') as channel:
        stub = kiki_core_pb2_grpc.ValueEngineStub(channel)
        prediction = await stub.PredictLTV(kiki_core_pb2.DataRequest(user_id=user_id, features=data))
    # 2. Supervisor Logic: Decide if we should bid or engage
    decision = "Aggressive Bid" if prediction.ltv > 0.8 else "Standard Retention"
    # 3. Use LangChain to generate a plan (optional, can expand logic)
    llm = OpenAI()
    prompt = PromptTemplate(input_variables=["decision", "ltv"], template="Decision: {decision}\nLTV: {ltv}\nPlan:")
    chain = LLMChain(llm=llm, prompt=prompt)
    plan = chain.run({"decision": decision, "ltv": prediction.ltv})
    return {"strategy": decision, "ltv_score": prediction.ltv, "plan": plan}
