"""
Generate Story Tool

A FastAPI tool for generating picture stories based on user prompts.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from pathlib import Path
from app.core.interfaces import ToolInterface
from app.llm.manager import get_model
import yaml
import textwrap

from .schemas import (
    GenerateStoryRequest,
    GenerateStoryResponse,
    Story,
    StoryScene,
    OutputSchema
)
from .image_generator import image_generator
from .prompts.story_generation import (
    STORY_GENERATION_PROMPT,
    IMAGE_GENERATION_PROMPT,
    STORY_VALIDATION_PROMPT
)


class GenerateStoryTool(ToolInterface):
    """Tool for generating picture stories"""
    
    # Required class variables for ToolInterface
    name = "generate_story"
    description = "Generate picture stories based on user prompts with multiple scenes and image descriptions"
    
    def __init__(self):
        self.router = APIRouter(prefix="/generate-story", tags=["story-generation"])
        self._setup_routes()
        self.prompts = self._load_prompts()
    
    def _setup_routes(self):
        """Set up the API routes"""
        
        @self.router.post("/create", response_model=GenerateStoryResponse)
        async def create_story(request: GenerateStoryRequest) -> GenerateStoryResponse:
            """
            Generate a picture story based on user input
            """
            try:
                logger.info(f"Generating story for user: {request.username}")
                logger.info(f"Prompt: {request.prompt}")
                
                # Generate the story
                story_data = await self._generate_story(request)
                
                # Create response
                response = GenerateStoryResponse(
                    success=True,
                    data=story_data,
                    metadata={
                        "generated_at": datetime.now().isoformat(),
                        "user": request.username,
                        "genre": request.genre,
                        "age_group": request.age_group,
                        "scene_count": request.scene_count
                    }
                )
                
                logger.info(f"Story generated successfully for {request.username}")
                return response
                
            except Exception as e:
                logger.error(f"Error generating story: {str(e)}")
                return GenerateStoryResponse(
                    success=False,
                    error=f"Failed to generate story: {str(e)}"
                )
        
        @self.router.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "tool": "generate-story"}
    
    async def _generate_story(self, request: GenerateStoryRequest) -> Story:
        """
        Generate a story using LLM
        """
        try:
            # Use the new LLM-based story generation
            story = await self._generate_story_with_llm(request)
            
            # Validate the story structure
            await self._validate_story(story, request)
            
            return story
            
        except Exception as e:
            logger.error(f"Error in story generation: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _generate_mock_story(self, request: GenerateStoryRequest) -> Story:
        """
        Generate a mock story for testing
        """
        scenes = []
        for i in range(request.scene_count):
            scene = StoryScene(
                id=i + 1,
                description=f"Scene {i + 1}: {self._get_scene_description(i + 1, request.prompt)}",
                imagePrompt=f"{request.prompt} - scene {i + 1}, {self._get_image_prompt(i + 1)}, {request.genre} style, colorful, detailed"
            )
            scenes.append(scene)
        
        return Story(
            title=f"Adventure of {request.prompt}",
            scenes=scenes
        )
    
    def _get_scene_description(self, scene_id: int, prompt: str) -> str:
        """Get scene description based on scene number"""
        descriptions = {
            1: "The beginning of our adventure",
            2: "The journey begins",
            3: "A challenge appears",
            4: "Overcoming obstacles",
            5: "The happy ending"
        }
        return descriptions.get(scene_id, f"Scene {scene_id} of the story")
    
    def _get_image_prompt(self, scene_id: int) -> str:
        """Get image prompt based on scene number"""
        prompts = {
            1: "beginning, colorful, detailed",
            2: "journey, adventure, vibrant",
            3: "challenge, dramatic, intense",
            4: "victory, triumph, bright",
            5: "ending, happy, peaceful"
        }
        return prompts.get(scene_id, "scene, colorful, detailed")
    
    async def _validate_story(self, story: Story, request: GenerateStoryRequest):
        """
        Validate the generated story
        """
        # Check scene count
        if len(story.scenes) != request.scene_count:
            raise ValueError(f"Expected {request.scene_count} scenes, got {len(story.scenes)}")
        
        # Check each scene has required fields
        for scene in story.scenes:
            if not scene.description or not scene.imagePrompt:
                raise ValueError(f"Scene {scene.id} missing required fields")
        
        # TODO: Add more validation logic
        logger.info("Story validation passed")
    
    async def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM with a prompt
        TODO: Integrate with actual LLM service
        """
        # Placeholder for LLM integration
        logger.info("LLM call would happen here")
        return "Mock LLM response"
    
    @classmethod
    def get_input_schema(cls):
        """Get the input schema for this tool."""
        return GenerateStoryRequest

    @classmethod
    def get_output_schema(cls):
        """Get the output schema for this tool."""
        return GenerateStoryResponse

    async def execute(self, input_data: GenerateStoryRequest, token: Optional[Dict[str, Any]] = None) -> OutputSchema:
        """
        Execute the tool with the given input data.
        
        Args:
            input_data: Validated input data for story generation
            token: Optional authentication token information
            
        Returns:
            Output schema with LLM result
        """
        try:
            logger.info(f"Executing generate story tool for user: {input_data.username}")
            logger.info(f"Prompt: {input_data.prompt}")
            
            llm_client = get_model()
            prompt_type = "summarize" 
            prompt = self.prompts[prompt_type]
            logger.info(f"Using prompt type: {prompt_type}")
            
            # Format the prompt with input data
            formatted_prompt = f"{prompt['system']}\n\n{prompt['human'].format(prompt=input_data.prompt, username=input_data.username, age_group=input_data.age_group, genre=input_data.genre, scene_count=input_data.scene_count)}"
            
            logger.info(f"Executing LLM with formatted prompt")
            try:
                result = await llm_client.invoke(formatted_prompt)
                logger.info(f"LLM response received, length: {len(result)}")
            
                # Check if result is empty or None
                if not result or result.strip() == "":
                    logger.warning("LLM returned empty response, using fallback")
                    return await self._generate_story_with_images(input_data)
                
                # Parse the LLM response to get story structure
                try:
                    logger.info("Parsing LLM response as JSON")
                    story_data = json.loads(result)
                    logger.info("Successfully parsed LLM response")
                    
                    # Generate images for each scene
                    scenes = story_data.get('scenes', [])
                    logger.info(f"Generating images for {scenes} scenes")
                    for scene in scenes: 
                        scene_text = scene.get('story_text', '')
                        if scene_text:
                            # Generate image for this scene
                            logger.info(f"Generating image for scene {scene.get('scene_number', 'unknown')}")
                            image_data = await image_generator.generate_image(
                                prompt=scene_text,
                                style=story_data.get('animated','theme', 'digital art')
                            )
                            if image_data:
                                scene['image'] = image_data
                            else:
                                # Fallback if image generation fails
                                scene['image'] = await image_generator.generate_image(
                                    prompt=input_data.prompt,
                                    style='digital art'
                                )
                        scene_image = scene.get('image', None)
                        if scene_image:
                            scene['image'] = scene_image
                        else:
                            scene['image'] = await image_generator.generate_image(
                                    prompt=input_data.prompt,
                                    style='digital art'
                                )

                    logger.info("All scene images generated successfully")
                    logger.info(f"Story data: {story_data}")
                    # Return the enhanced story with images
                    return OutputSchema(result=json.dumps(story_data))
                    
                except json.JSONDecodeError as parse_error:
                    logger.warning(f"Failed to parse LLM response as JSON: {parse_error}")
                    logger.warning(f"Raw LLM response: {result}")
                    
                    # Try to extract JSON from the response (sometimes LLM adds extra text)
                    try:
                        # Look for JSON-like content between curly braces
                        import re
                        json_match = re.search(r'\{.*\}', result, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(0)
                            
                            # Fix common LLM JSON issues
                            # 1. Add missing commas between array elements (scenes)
                            json_str = re.sub(r'}\s*{\s*"scene_number"', '},{"scene_number"', json_str)
                            # 2. Fix missing commas in object arrays
                            json_str = re.sub(r'}\s*}\s*]', '}]', json_str)
                            # 3. Fix trailing commas
                            json_str = re.sub(r',\s*}', '}', json_str)
                            json_str = re.sub(r',\s*]', ']', json_str)
                            
                            story_data = json.loads(json_str)
                            logger.info("Successfully extracted and fixed JSON from LLM response")
                        else:
                            raise ValueError("No JSON found in response")
                    except Exception as extract_error:
                        logger.warning(f"Failed to extract JSON from response: {extract_error}")
                        # Generate a simple story with images
                        return await self._generate_story_with_images(input_data)
                    
            except Exception as llm_error:
                logger.warning(f"LLM call failed, using fallback: {str(llm_error)}")
                # Generate a simple story with images
                return await self._generate_story_with_images(input_data)

        except Exception as e:
            logger.error(f"Error executing generate story tool: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to execute tool: {str(e)}")

    async def _generate_story_with_llm(self, request: GenerateStoryRequest) -> Story:
        """
        Generate a story using LLM with proper prompt engineering
        """
        try:
            # Get the LLM model
            llm_client = get_model()
            
            # Format the story generation prompt
            formatted_prompt = STORY_GENERATION_PROMPT.format(
                username=request.username,
                prompt=request.prompt,
                genre=request.genre,
                age_group=request.age_group,
                scene_count=request.scene_count
            )
            
            logger.info(f"Generating story with LLM for prompt: {request.prompt}")
            
            # Build the LangChain chain
            chain = (
                ChatPromptTemplate.from_messages([
                    ("system", "You are a creative storyteller who creates engaging picture stories."),
                    ("human", formatted_prompt)
                ])
                | llm_client
                | StrOutputParser()
            )
            
            # Execute the chain
            result = await chain.ainvoke({})
            
            logger.info(f"LLM response received, length: {len(result)}")
            
            # Parse the JSON response
            try:
                story_json = json.loads(result)
                logger.info("Successfully parsed JSON response from LLM")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from LLM response: {e}")
                logger.info("Falling back to mock story generation")
                return await self._generate_mock_story(request)
            
            # Validate and create story object
            story = await self._parse_llm_response(story_json, request)
            
            # Validate the story structure
            await self._validate_story(story, request)
            
            return story
            
        except Exception as e:
            logger.error(f"Error in LLM story generation: {str(e)}")
            logger.info("Falling back to mock story generation")
            return await self._generate_mock_story(request)



    async def _parse_llm_response(self, story_json: Dict[str, Any], request: GenerateStoryRequest) -> Story:
        """
        Parse the LLM response and create a Story object
        """
        try:
            # Extract title and scenes from LLM response
            title = story_json.get("title", f"Adventure of {request.prompt}")
            scenes_data = story_json.get("scenes", [])
            
            scenes = []
            for i, scene_data in enumerate(scenes_data):
                scene = StoryScene(
                    id=i + 1,
                    description=scene_data.get("description", f"Scene {i + 1}"),
                    imagePrompt=scene_data.get("imagePrompt", f"{request.prompt} - scene {i + 1}")
                )
                scenes.append(scene)
            
            # Ensure we have the minimum number of scenes
            while len(scenes) < request.scene_count:
                scene = StoryScene(
                    id=len(scenes) + 1,
                    description=f"Scene {len(scenes) + 1}: {self._get_scene_description(len(scenes) + 1, request.prompt)}",
                    imagePrompt=f"{request.prompt} - scene {len(scenes) + 1}, {self._get_image_prompt(len(scenes) + 1)}, {request.genre} style, colorful, detailed"
                )
                scenes.append(scene)
            
            return Story(
                title=title,
                scenes=scenes[:request.scene_count]  # Ensure we don't exceed requested scene count
            )
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            raise ValueError(f"Failed to parse LLM response: {str(e)}")

    def get_router(self) -> APIRouter:
        """Get the FastAPI router for this tool"""
        return self.router
    
    async def _generate_story_with_images(self, input_data: GenerateStoryRequest) -> OutputSchema:
        """
        Generate a simple story with images when LLM fails
        """
        try:
            scenes = []
            scene_descriptions = [
                f"Scene 1: The beginning of {input_data.prompt}",
                f"Scene 2: The adventure continues with {input_data.prompt}",
                f"Scene 3: A challenge appears in {input_data.prompt}",
                f"Scene 4: Overcoming obstacles in {input_data.prompt}",
                f"Scene 5: The happy ending of {input_data.prompt}"
            ]
            
            for i, description in enumerate(scene_descriptions, 1):
                # Generate image for each scene
                image_data = await image_generator.generate_image(
                    prompt=description,
                    style=input_data.genre
                )
                
                scenes.append({
                    "scene_number": i,
                    "story_text": description,
                    "image": image_data
                })
            
            story_data = {
                "title": f"Adventure of {input_data.prompt}",
                "theme": input_data.genre,
                "target_age": f"{input_data.age_group} years",
                "scenes": scenes
            }
            
            logger.info(f"Generated simple story with {story_data} scenes")

            return OutputSchema(result=json.dumps(story_data))
            
        except Exception as e:
            logger.error(f"Error generating story with images: {str(e)}")
            # Ultimate fallback - return basic structure
            fallback_result = {
                "title": f"Story of {input_data.prompt}",
                "theme": "adventure",
                "target_age": "5-10 years",
                "scenes": [
                    {
                        "scene_number": 1,
                        "story_text": f"A beautiful scene showing {input_data.prompt}",
                        "image": await image_generator.generate_image(input_data.prompt, "digital art")
                    }
                ]
            }
            return OutputSchema(result=json.dumps(fallback_result))

    def _load_prompts(self) -> Dict[str, Any]:
        """
        Load prompts from YAML files in the prompts directory.

        Returns:
            Dictionary mapping prompt types to prompt templates
        """
        prompts = {}
        prompts_dir = Path(__file__).parent / "prompts"

        if not prompts_dir.exists():
            raise ValueError("Prompts directory not found for the tool")

        # Load each YAML file in the prompts directory
        for prompt_file in prompts_dir.glob("*.yaml"):
            try:
                with open(prompt_file, "r") as f:
                    prompt_data = yaml.safe_load(f)

                prompt_type = prompt_file.stem  # Use filename as prompt type

                if "system" in prompt_data:
                    prompt_data["system"] = textwrap.dedent(prompt_data["system"]).strip()
                if "human" in prompt_data:
                    prompt_data["human"] = textwrap.dedent(prompt_data["human"]).strip()

                prompts[prompt_type] = prompt_data
            except Exception as e:
                raise ValueError(f"Error loading prompt file {prompt_file}: {str(e)}")

        if not prompts:
            raise ValueError("No valid prompts found")

        return prompts


# Create tool instance
generate_story_tool = GenerateStoryTool()
