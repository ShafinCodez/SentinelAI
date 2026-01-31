from fastapi import FastAPI, BackgroundTasks
from core.orchestration import ScanOrchestrator
from pydantic import BaseModel

app = FastAPI(title="SentinelAI API", version="1.0")

class ScanRequest(BaseModel):
    path: str

@app.get("/")
def health_check():
    return {"status": "active", "system": "SentinelAI"}

@app.post("/scan")
async def trigger_scan(request: ScanRequest):
    # In a real app, this would push to Celery
    orchestrator = ScanOrchestrator()
    findings = await orchestrator.scan_directory(request.path)
    return {"status": "complete", "findings_count": len(findings), "findings": findings}
