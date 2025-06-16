from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage
)

class OnboardingState(BaseModel):
    messages: List[Union[HumanMessage, AIMessage, SystemMessage, ToolMessage]] = Field(default_factory=list)
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    current_step: Optional[str] = Field(default=None)
    query_results: Optional[Dict[str, Any]] = Field(default=None)