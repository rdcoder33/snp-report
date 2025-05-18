from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
from app_agent import get_agent_and_state
import time
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    file_content: str
    user_profile: str = None
    file_type: str = None

@app.api_route("/stream-report", methods=["GET", "POST"])
async def stream_report(request: Request):
    if request.method == "GET":
        # Provide default or query param values for file_path and personalization_data
        file_content = request.query_params.get("file_content", "/Users/winkltechnologies/Desktop/gene-report/data/genome_Joshua_Yoakem_v5_Full_20250129211749.txt")
        user_profile = request.query_params.get("user_profile", None)
    else:
        body = await request.json()
        file_content = body.get("file_content")
        user_profile = body.get("user_profile")

    agent, state = get_agent_and_state(
        file_content=file_content,
        user_profile=user_profile,
        file_type= request.query_params.get("file_type", "type_23andme")
    )
    config = {"configurable": {"thread_id": str(
        int(time.time() * 1000 + (time.time() % 1) * 1000))}}

    async def event_stream():
        async for update in agent.astream(state, config, stream_mode="updates"):
            # Convert Pydantic models to dicts for JSON serialization
            if hasattr(update, "model_dump"):
                update = update.model_dump()
            elif hasattr(update, "dict"):
                update = update.dict()
            yield f"data: {json.dumps(update)}\n\n"
            await asyncio.sleep(0)
        yield "data: {\"event\": \"end\", \"data\": \"done\"}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
