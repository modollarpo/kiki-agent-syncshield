

import structlog
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import grpc
import torch
from model.ltv_net import LTVNet
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../shared/types/python')))
import kiki_core_pb2
import kiki_core_pb2_grpc
from concurrent import futures

structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = structlog.get_logger()


app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health():
    return {"status": "ok"}

# Dependency Injection: Model loader
def get_model():
    # In production, load a trained model from disk
    return LTVNet(10, 20, 2, 1)

# gRPC server implementation
class ValueEngineServicer(kiki_core_pb2_grpc.ValueEngineServicer):
    def __init__(self, model):
        self.model = model

    def PredictLTV(self, request, context):
        features = torch.tensor(request.features, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        ltv = self.model(features).item()
        return kiki_core_pb2.LTVResult(ltv=ltv, model_version="v0.1")

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    kiki_core_pb2_grpc.add_ValueEngineServicer_to_server(ValueEngineServicer(get_model()), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    import threading
    threading.Thread(target=serve_grpc, daemon=True).start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
