import textwrap
import yaml
from pathlib import Path
from typing import Dict, Any

from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

from app.core.interfaces import ToolInterface
from app.llm.manager import get_model
from .schemas import InputSchema, OutputSchema


class TextProcessorTool(ToolInterface):
    """Sample tool that uses LLM to process text."""

    name = "query_summarizer"
    description = "Processes text using the LLM"

    def __init__(self):
        """Initialize the tool and load prompts."""
        self.prompts = self._load_prompts()

    @classmethod
    def get_input_schema(cls):
        """Get the input schema for this tool."""
        return InputSchema

    @classmethod
    def get_output_schema(cls):
        """Get the output schema for this tool."""
        return OutputSchema

    async def execute(self, input_data: InputSchema, token=None) -> OutputSchema:
        """
        Execute the tool with the given input data.

        Args:
            input_data: Tool input
            token: Optional authentication token

        Returns:
            Processed text from the LLM
        """
        llm_client = get_model()

        # Get the prompt type from input or default to summarize
        prompt_type = input_data.prompt_type or "summarize"
        if prompt_type not in self.prompts:
            raise ValueError(f"Invalid prompt type: {prompt_type}")

        prompt = self.prompts[prompt_type]

        # Build the LangChain chain
        chain = (
            ChatPromptTemplate.from_messages(
                [("system", prompt["system"]), ("human", prompt["human"])]
            )
            | llm_client
            | StrOutputParser()
        )

        # Format the prompt with the input text
        formatted_prompt = {"text": input_data.text, "max_length": input_data.max_length}

        # Execute the chain
        result = await chain.ainvoke(formatted_prompt)

        # Return the result
        return OutputSchema(
            processed_text=result,
            original_length=len(input_data.text),
            processed_length=len(result),
        )

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
