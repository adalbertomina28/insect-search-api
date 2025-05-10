from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    insect_id: Optional[int] = None
    insect_name: Optional[str] = None
    language: Optional[str] = "es"  # Idioma por defecto: español

class ChatMessageResponse(BaseModel):
    role: str
    content: str
    refusal: Optional[str] = None
    reasoning: Optional[str] = None

class ChatChoice(BaseModel):
    index: int
    message: ChatMessageResponse
    finish_reason: str
    native_finish_reason: Optional[str] = None
    logprobs: Optional[Any] = None

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: Optional[Any] = None

class ChatCompletionResponse(BaseModel):
    id: str
    provider: str
    model: str
    object: str
    created: int
    choices: List[ChatChoice]
    usage: TokenUsage
