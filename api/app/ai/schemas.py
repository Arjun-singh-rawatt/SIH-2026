"""Internal schemas and prompt structures for AI NLP pipeline."""

from typing import List, Optional
from pydantic import BaseModel, Field


class PromptTemplate(BaseModel):
    system_instruction: str
    user_template: str
    temperature: float = 0.1
    max_tokens: int = 1000
