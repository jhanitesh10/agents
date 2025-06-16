from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class ResearchState(BaseModel):
    messages: List[Any] = []
    questions: List[Dict[str, Any]] = []
    current_step: Optional[str] = None
    query_results: Optional[Dict[str, Any]] = None