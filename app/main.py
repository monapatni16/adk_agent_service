import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.config import settings
from app.utils import logger
from app.agents import create_agents
from app.orchestrator import Orchestrator

app = FastAPI(title=settings.APP_NAME)

agents = create_agents()
orchestrator = Orchestrator(agents)

@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}

@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return PlainTextResponse(content=data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

@app.post("/process")
async def process(request: Request):
    try:
        body = await request.json()
        query = body.get("query")
        if not query or not isinstance(query, str) or len(query.strip()) < 1:
            raise HTTPException(status_code=400, detail="Invalid 'query' in request")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Invalid request body", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid request body")

    return StreamingResponse(orchestrator.stream_workflow(query), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)