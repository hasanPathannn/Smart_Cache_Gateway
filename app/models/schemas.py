from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    prompt: str = Field(..., example="What is the capital of France?")
    user_id: str = Field(default="anonymous", example="user_123")
    
class ChatResponse(BaseModel):
    response: str
    source: str
    latency_saved: Optional[str] = None
    cost_incurred: Optional[bool] = False