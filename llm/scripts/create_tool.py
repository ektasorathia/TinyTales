#!/usr/bin/env python
"""
Tool creation script.

This script creates a new tool from a template.
"""
import sys
from pathlib import Path
import textwrap
from loguru import logger


def create_tool(tool_name: str):
    """
    Create a new tool from the template.

    Args:
        tool_name: Name of the tool to create

    Returns:
        bool: True if the tool was created successfully, False otherwise
    """
    # Sanitize tool name
    tool_name = tool_name.lower().replace(" ", "_").replace("-", "_")

    # Get the tools directory path
    tools_dir = Path.cwd() / "tools"
    if not tools_dir.exists():
        tools_dir.mkdir(parents=True)

    # Check if the tool already exists
    tool_dir = tools_dir / tool_name
    if tool_dir.exists():
        logger.error(f"Tool '{tool_name}' already exists")
        return False

    # Create the tool directory
    tool_dir.mkdir()

    # Create __init__.py
    with open(tool_dir / "__init__.py", "w") as f:
        f.write("# Tool package\n")

    # Create schemas.py
    with open(tool_dir / "schemas.py", "w") as f:
        f.write(
            textwrap.dedent(
                f'''
                from typing import Optional
                from pydantic import BaseModel, Field


                class InputSchema(BaseModel):
                    """
                    Input schema for the {tool_name} tool.

                    TODO: CUSTOMIZE THIS SCHEMA
                    This is a minimal placeholder schema. You should modify it to include all the
                    fields your tool needs as input, with appropriate types and validation.
                    """

                    query: str = Field(
                        ...,
                        description="The input query",
                        min_length=1
                    )

                    # Add your custom fields here
                    # e.g.:
                    # max_results: int = Field(10, description="Maximum number of results to return", ge=1, le=100)
                    # include_metadata: bool = Field(False, description="Whether to include metadata in results")


                class OutputSchema(BaseModel):
                    """
                    Output schema for the {tool_name} tool.

                    TODO: CUSTOMIZE THIS SCHEMA
                    This is a minimal placeholder schema. You should modify it to include all the
                    fields your tool returns as output, with appropriate types.
                    """

                    result: str = Field(
                        ...,
                        description="The result of the operation"
                    )

                    # Add your custom fields here
                    # e.g.:
                    # execution_time: float = Field(..., description="Time taken to execute the tool in seconds")
                    # source: Optional[str] = Field(None, description="Source of the result")
                '''
            ).strip()
        )

    # Create tool.py
    with open(tool_dir / "tool.py", "w") as f:
        class_name = "".join(word.capitalize() for word in tool_name.split("_"))
        f.write(
            textwrap.dedent(
                f'''
                from app.core.interfaces import ToolInterface
                from .schemas import InputSchema, OutputSchema


                class {class_name}Tool(ToolInterface):
                    """
                    {tool_name.replace('_', ' ').title()} tool implementation.

                    [Add your tool description here]
                    """

                    name = "{tool_name}"
                    description = "Tool for {tool_name.replace('_', ' ')}"

                    @classmethod
                    def get_input_schema(cls):
                        """Get the input schema for this tool."""
                        # IMPORTANT: Review and customize the InputSchema in schemas.py to match your tool's requirements
                        # The default schema only provides a basic 'query' field which may not be sufficient
                        return InputSchema

                    @classmethod
                    def get_output_schema(cls):
                        """Get the output schema for this tool."""
                        # IMPORTANT: Review and customize the OutputSchema in schemas.py to match your tool's requirements
                        # The default schema only provides a basic 'result' field which may not be sufficient
                        return OutputSchema

                    async def execute(self, input_data: InputSchema, token=None) -> OutputSchema:
                        """
                        Execute the tool with the given input data.

                        Args:
                            input_data: The validated input data
                            token: Optional authentication token

                        Returns:
                            The tool output
                        """
                        # TODO: Implement your tool logic here
                        raise NotImplementedError(
                            "Tool logic not implemented. Please replace this with your implementation."
                        )

                        # Example implementation:
                        # result = f"Processed: {{input_data.query}}"
                        # return OutputSchema(result=result)
                '''
            ).strip()
        )

    # Create config.toml
    with open(tool_dir / "config.toml", "w") as f:
        f.write(
            textwrap.dedent(
                f"""
            # Tool configuration for {tool_name}

            [tool]
            name = "{tool_name.replace('_', ' ').title()}"
            description = "Tool for {tool_name.replace('_', ' ')}"
            version = "0.1.0"
            uses_llm = false

            [settings]
            # Add tool-specific settings here
            timeout = 30
            """
            ).strip()
        )

    # Create prompts directory (if the tool might use LLM)
    prompts_dir = tool_dir / "prompts"
    prompts_dir.mkdir()

    # Create a sample prompt
    with open(prompts_dir / "default.yaml", "w") as f:
        f.write(
            textwrap.dedent(
                """
            system: |
              You are a helpful assistant specialized in processing user queries.
              Provide concise, accurate  responses based on the input provided.

            human: |
              Please process the following query:

              {query}
            """
            ).strip()
        )

    # Create tests directory
    tests_dir = tool_dir / "tests"
    tests_dir.mkdir()

    # Create a basic test file
    with open(tests_dir / f"test_{tool_name}.py", "w") as f:
        class_name = "".join(word.capitalize() for word in tool_name.split("_"))
        f.write(
            textwrap.dedent(
                f'''
            import pytest
            from ..tool import {class_name}Tool
            from ..schemas import InputSchema, OutputSchema


            @pytest.mark.asyncio
            async def test_{tool_name}_execution():
                """Test basic execution of the tool."""
                # Create an instance of the tool
                tool = {class_name}Tool()

                # Create test input
                input_data = InputSchema(query="test query")

                # Execute the tool
                result = await tool.execute(input_data)

                # Assert the result
                assert isinstance(result, OutputSchema)
                assert result.result is not None
                assert "test query" in result.result
            '''
            ).strip()
        )

    logger.success(f"Tool '{tool_name}' created successfully!")
    logger.info(f"Tool directory: {tool_dir}")
    logger.info("\nNext steps:")
    logger.info("1. Implement your tool logic in tool.py")
    logger.info("2. Update the input and output schemas in schemas.py")
    logger.info("3. Add any tool-specific configuration in config.toml")
    logger.info("4. Write tests in the tests directory")

    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/create_tool.py <tool_name>")
        sys.exit(1)

    tool_name = sys.argv[1]
    if create_tool(tool_name):
        sys.exit(0)
    else:
        sys.exit(1)
