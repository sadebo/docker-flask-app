from fastapi import FastAPI, Request
from vllm import LLM, SamplingParams
from prometheus_client import start_http_server, Gauge
import os

MODEL_NAME = os.getenv("MODEL_NAME", "facebook/opt-125m")
app = FastAPI(title="vLLM CPU Server")

llm = LLM(model=MODEL_NAME)
active_requests = Gauge("vllm_requests_active", "Number of active inference requests")

@app.get("/healthz")
def health():
    return {"status": "ok", "model": MODEL_NAME}

@app.post("/v1/completions")
async def completions(req: Request):
    active_requests.inc()
    try:
        data = await req.json()
        prompt = data.get("prompt")
        params = SamplingParams(max_tokens=data.get("max_tokens", 64))
        outputs = llm.generate([prompt], params)
        return {"choices": [{"text": outputs[0].outputs[0].text}]}
    finally:
        active_requests.dec()

# Prometheus metrics server
start_http_server(9090)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
