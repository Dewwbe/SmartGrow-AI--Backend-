"""
Stub for the AI assistant agent. Deliberately thin: the real agent logic
(prompting, tool-calling into the tray/sensor/prediction services above,
conversation memory, etc.) is its own project -- this just gives the
Flutter app a stable endpoint and shape to build against from day one, and
gives you a single seam to plug a real LLM call into later.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import UserInDB

router = APIRouter(prefix="/agent", tags=["AI Agent"])


class AgentChatRequest(BaseModel):
    message: str
    tray_id: str | None = None


class AgentChatResponse(BaseModel):
    reply: str
    tray_id: str | None = None


@router.post("/chat", response_model=AgentChatResponse)
async def chat(
    payload: AgentChatRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    """
    TODO: replace this placeholder with a real LLM call (e.g. an Anthropic
    or OpenAI client) that has tool access to get_sensor_service /
    get_ml_service / get_irrigation_service so the agent can actually answer
    "should I water tray 7?" using live data, not just echo the question.
    """
    return AgentChatResponse(
        reply=f"(agent stub) Received: '{payload.message}'. Wire this endpoint up to your LLM of choice.",
        tray_id=payload.tray_id,
    )
