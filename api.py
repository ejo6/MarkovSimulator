from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from MarkovChain import MarkovChain, MarkovChainException

class EdgeRequest(BaseModel):
    fromNode: str
    toNode: str
    weight: float

class ChainRequest(BaseModel):
    edges: list[EdgeRequest]
    start: str
    iterations: int
    burnIn: int = 0
    write_interval: int = 0
    csv_path: str = "convergence.csv"

class ChainResponse(BaseModel):
    result: dict[str, int]
    proportions: dict[str, float]

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run", response_model=ChainResponse)
def run_chain(payload: ChainRequest):
    chain = MarkovChain()
    for edge in payload.edges:
        chain.addEdge(edge.fromNode, edge.toNode, edge.weight)
    if not chain.checkGraph():
        raise HTTPException(status_code=400, detail="Edge weights must sum to 1 for each node.")
    try:
        result, proportions = chain.runChainIterations(payload.iterations, payload.start, payload.burnIn, payload.write_interval, payload.csv_path)
    except MarkovChainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"result": result, "proportions": proportions}
