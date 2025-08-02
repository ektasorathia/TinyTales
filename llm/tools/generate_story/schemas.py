"""
Schemas for the Generate Story Tool
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class StoryScene(BaseModel):
    """Schema for a story scene"""
    id: int = Field(..., description="Scene number (1-5)")
    description: str = Field(..., description="Detailed description of the scene")
    imagePrompt: str = Field(..., description="Prompt for image generation")
    imageUrl: Optional[str] = Field(None, description="URL of the generated image")


class Story(BaseModel):
    """Schema for a complete story"""
    title: str = Field(..., description="Title of the story")
    scenes: List[StoryScene] = Field(..., description="List of story scenes (minimum 5)")


class GenerateStoryRequest(BaseModel):
    """Request schema for story generation"""
    username: str = Field(..., description="Name of the user creating the story")
    prompt: str = Field(..., description="User's story prompt/idea")
    genre: Optional[str] = Field("fantasy", description="Story genre (fantasy, adventure, mystery, etc.)")
    age_group: Optional[str] = Field("children", description="Target age group (children, young_adult, adult)")
    scene_count: Optional[int] = Field(5, description="Number of scenes to generate (minimum 5)")


class GenerateStoryResponse(BaseModel):
    """Response schema for story generation"""
    success: bool = Field(..., description="Whether the story generation was successful")
    data: Optional[Story] = Field(None, description="Generated story data")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    metadata: Optional[dict] = Field(None, description="Additional metadata about the generation")


class OutputSchema(BaseModel):
    """Output schema for the execute method"""
    result: str = Field(..., description="The result from the LLM execution")
