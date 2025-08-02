from typing import Optional
from pydantic import BaseModel, Field


class InputSchema(BaseModel):
    """Input schema for the text processor tool."""

    text: str = Field(..., description="The text to process", min_length=1, max_length=10000)
    max_length: int = Field(
        100, description="Maximum length of the processed text in words", ge=10, le=1000
    )
    prompt_type: Optional[str] = Field(
        None, description="Type of processing to perform (summarize, analyze, etc.)"
    )


class OutputSchema(BaseModel):
    """Output schema for the text processor tool."""

    processed_text: str = Field(..., description="The processed text")
    original_length: int = Field(..., description="Length of the original text in characters")
    processed_length: int = Field(..., description="Length of the processed text in characters")
