"""
Main application module for the FastAPI Tools framework.

This module creates and configures the FastAPI application, discovers and registers
tools, and sets up middleware and dependencies.
"""

from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime

from loguru import logger
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.config import get_config
from app.core.discovery import get_registry


# Request model for the generate-story endpoint
class GenerateStoryRequest(BaseModel):
    """Request model for story generation"""
    username: str
    prompt: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle management for the FastAPI application.

    This function handles initialization and cleanup of application resources.
    """
    try:
        # Initialize components
        logger.info("Starting application")

        # Initialize LLM if enabled
        config = get_config()
        if config.get("llm.enabled", False):
            try:
                from app.llm.manager import ModelManager

                logger.info("Initializing ModelManager")
                ModelManager.initialize()
                logger.info("ModelManager initialized successfully")
            except ImportError:
                logger.error(
                    "LLM functionality requested but required dependencies are not installed."
                )
                logger.error("Please install LLM dependencies: pip install '.[llm]'")

        # Discover and register tools
        registry = get_registry()
        logger.info("Discovering tools...")
        registry.discover_tools()
        registry.register_routes(app)

        yield
    except Exception as e:
        logger.critical(f"Error during application startup: {e}")
        raise
    finally:
        # Cleanup resources
        logger.info("Shutting down application")
        if config.get("llm.enabled", False):
            try:
                from app.llm.manager import ModelManager

                logger.info("Cleaning up ModelManager")
                ModelManager.clear()
            except ImportError:
                # Already logged the error during initialization
                pass


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        The configured FastAPI application
    """
    # Load configuration
    app_config = get_config()

    # Determine auth dependencies
    auth_dependencies = []
    if app_config.get("auth.enabled", False):
        try:
            from app.auth.sso import get_auth_dependencies

            auth_dependencies = get_auth_dependencies()
            logger.info(f"Using {len(auth_dependencies)} auth dependencies")
        except ImportError:
            logger.error("Authentication requested but required dependencies are not installed.")
            logger.error("Please install authentication dependencies: pip install '.[auth]'")

    # Create FastAPI app
    app = FastAPI(
        title=app_config.get("app.name", "FastAPI Tools"),
        description=app_config.get(
            "app.description", "A collection of tools exposed as FastAPI endpoints"
        ),
        version=app_config.get("app.version", "0.1.0"),
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.get("server.cors.origins", ["*"]),
        allow_credentials=app_config.get("server.cors.allow_credentials", True),
        allow_methods=app_config.get("server.cors.allow_methods", ["*"]),
        allow_headers=app_config.get("server.cors.allow_headers", ["*"]),
    )

    # Set up authentication if enabled
    if app_config.get("auth.enabled", False):
        try:
            from app.auth.sso import setup_auth

            setup_auth(app)
        except ImportError:
            # Already logged the error during auth dependencies setup
            pass

    # Add a simple root endpoint (with authentication if enabled)
    @app.get("/", tags=["status"], dependencies=auth_dependencies)
    async def root():
        """
        Root endpoint that returns basic information about the application.
        """
        return {
            "name": app_config.get("app.name"),
            "version": app_config.get("app.version"),
            "description": app_config.get("app.description"),
        }

    # Add generate-story endpoint
    @app.post("/generate-story", tags=["story-generation"], dependencies=auth_dependencies)
    async def generate_story(request: GenerateStoryRequest):
        """
        Generate a story based on user prompt and username.
        Uses default values: age_group=3, scene_count=5, genre=kids
        """
        try:
            logger.info(f"Generating story for user: {request.username}")
            logger.info(f"Prompt: {request.prompt}")
            
            # Import the GenerateStoryTool and schemas
            from tools.generate_story.tool import GenerateStoryTool
            from tools.generate_story.schemas import GenerateStoryRequest as ToolRequest, Story
            
            # Create tool instance
            tool = GenerateStoryTool()
            
            # Create tool request with default values
            tool_request = ToolRequest(
                username=request.username,
                prompt=request.prompt,
                age_group="3",  # Default to age group 3
                scene_count=5,  # Default to 5 scenes
                genre="kids"    # Default to kids genre
            )
            
            # Generate the story
            story_data = await tool.execute(tool_request)
            
            # Return the response in the expected format
            return {
                "success": True,
                "data": story_data,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "user": request.username,
                    "genre": "kids",
                    "age_group": "3",
                    "scene_count": 5
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate story: {str(e)}")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    config = get_config()
    uvicorn.run(
        "app.main:app",
        host=config.get("server.host", "0.0.0.0"),
        port=config.get("server.port", 8000),
        reload=config.get("server.reload", False),
    )
