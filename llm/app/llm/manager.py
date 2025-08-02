from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from loguru import logger
import httpx
import json
from langchain_openai import ChatOpenAI


class OllamaClient:
    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def invoke(self, prompt: str) -> str:
        """Invoke Ollama with a prompt"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise


@dataclass
class ModelConfig:
    use_ollama: bool
    chomsky_model_name: str
    max_tokens: int
    temperature: float
    ollama_model: Optional[str]
    ollama_base_url: Optional[str]
    chgw_endpoint: Optional[str]
    enable_prompt_logging: bool


def get_config() -> ModelConfig:
    """
    Get LLM configuration from the application config.

    This will be integrated with the framework's configuration system.
    """
    from app.core.config import get_config as get_app_config

    config = get_app_config()
    llm_config = config.get("llm", {})
    print(f"LLM Config: {llm_config}")
    return ModelConfig(
        use_ollama=llm_config.get("use_ollama", True),
        chomsky_model_name=llm_config.get("model_name", "gpt-4"),
        max_tokens=llm_config.get("max_tokens", 1000),
        temperature=llm_config.get("temperature", 0.7),
        ollama_model=llm_config.get("ollama_model", "llama4:16x17b"),
        ollama_base_url=llm_config.get("ollama_base_url", "http://localhost:11434"),
        chgw_endpoint=llm_config.get("endpoint"),
        enable_prompt_logging=llm_config.get("enable_prompt_logging", False),
    )


class ModelManager:
    _instance: Union[OllamaClient, ChatOpenAI] = None

    @classmethod
    def initialize(cls) -> None:
        if cls._instance is None:
            config = get_config()
            logger.info(f"Initializing model with config: {config}")
            try:
                if config.use_ollama:
                    if not config.ollama_model:
                        raise ValueError(
                            "OLLAMA_MODEL must be set in configuration when using Ollama"
                        )
                    if not config.ollama_base_url:
                        raise ValueError("OLLAMA_BASE_URL must be provided when using Ollama")
                    logger.info("Initializing Ollama client")
                    
                    cls._instance = OllamaClient(
                        model=config.ollama_model,
                        base_url=config.ollama_base_url
                    )
                else:
                    # Use OpenAI as default
                    logger.info("Initializing OpenAI model")
                    import os
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        raise ValueError("OPENAI_API_KEY environment variable must be set")
                    
                    cls._instance = ChatOpenAI(
                        model=config.chomsky_model_name,
                        max_tokens=config.max_tokens,
                        temperature=config.temperature,
                    )
                logger.info("Model initialized successfully")
            except Exception as e:
                logger.critical(f"Failed to initialize model: {e}")
                raise RuntimeError("Failed to initialize the language model.") from e

    @classmethod
    def get_model(cls) -> Union[OllamaClient, ChatOpenAI]:
        if cls._instance is None:
            raise RuntimeError(
                "Model has not been initialized. Call ModelManager.initialize() first."
            )
        return cls._instance

    @classmethod
    def clear(cls) -> None:
        if cls._instance is not None:
            cls._instance = None


def get_model():
    """
    Get the initialized language model.
    """
    return ModelManager.get_model()
