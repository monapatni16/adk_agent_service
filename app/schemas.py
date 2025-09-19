from pydantic import BaseModel, Field
from typing import Optional, Any, List

class ProcessRequest(BaseModel):
    query: str = Field(..., min_length=1)

class AgentProgress(BaseModel):
    status: str  # “started”, “completed”, “failed”
    current_agent: Optional[str] = None
    step_index: Optional[int] = None
    total_steps: Optional[int] = None
    message: Optional[str] = None
    data: Optional[Any] = None

class FinalResult(BaseModel):
    workflow: str
    steps: List[AgentProgress]
    final_output: Optional[str]