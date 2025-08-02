"""
Core interfaces for tool implementation.

This module defines the base interfaces that all tools must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Type, TypeVar, Optional

from pydantic import BaseModel

# Type variables for input and output schemas
InputSchemaT = TypeVar("InputSchemaT", bound=BaseModel)
OutputSchemaT = TypeVar("OutputSchemaT", bound=BaseModel)


class ToolInterface(ABC):
    """
    Base interface that all tools must implement.

    Each tool must define:
    - name: A unique identifier for the tool
    - description: A human-readable description of what the tool does
    - An execute method that processes input data and returns output data
    - Schema methods that return Pydantic models for input/output validation
    """

    # Class variables that must be defined by all tools
    name: ClassVar[str]
    description: ClassVar[str]

    @abstractmethod
    async def execute(
        self, input_data: InputSchemaT, token: Optional[Dict[str, Any]] = None
    ) -> OutputSchemaT:
        """
        Execute the tool with the given input data.

        Args:
            input_data: Validated input data conforming to the tool's input schema
            token: Optional authentication token information

        Returns:
            Output data conforming to the tool's output schema

        Raises:
            Exception: Any error that occurs during execution
        """
        pass

    @classmethod
    @abstractmethod
    def get_input_schema(cls) -> Type[BaseModel]:
        """
        Get the Pydantic model for input validation.

        Returns:
            A Pydantic model class that defines the expected input structure
        """
        pass

    @classmethod
    @abstractmethod
    def get_output_schema(cls) -> Type[BaseModel]:
        """
        Get the Pydantic model for output validation.

        Returns:
            A Pydantic model class that defines the expected output structure
        """
        pass

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """
        Get metadata about the tool.

        This method can be overridden to provide additional metadata beyond
        the required name and description.

        Returns:
            A dictionary containing tool metadata
        """
        return {
            "name": cls.name,
            "description": cls.description,
        }
