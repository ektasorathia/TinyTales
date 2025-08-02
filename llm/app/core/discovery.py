"""
Tool discovery and registration system.

This module scans the tools directory, validates tool implementations,
and registers them with the FastAPI application.
"""

from typing import Dict, List, Type
from pathlib import Path
import importlib
import inspect
from loguru import logger

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from starlette.requests import Request

from app.core.interfaces import ToolInterface
from app.core.config import get_config


class ToolDiscoveryError(Exception):
    """Exception raised for errors during tool discovery."""


class ToolRegistry:
    """
    Registry for discovered tools.

    This class is responsible for:
    - Discovering tools in the tools directory
    - Validating that tools implement the required interface
    - Registering routes for each tool
    """

    def __init__(self):
        """Initialize the tool registry."""
        self.tools: Dict[str, Type[ToolInterface]] = {}
        self._router = APIRouter(prefix="/tools", tags=["tools"])

    def discover_tools(self, tools_dir: Path = None) -> Dict[str, Type[ToolInterface]]:
        """
        Discover all valid tools in the tools directory.

        Args:
            tools_dir: Path to the tools directory. If None, uses the default path.

        Returns:
            Dictionary mapping tool names to tool classes

        Raises:
            ToolDiscoveryError: If there's an error during tool discovery
        """
        base_dir = Path.cwd() if tools_dir is None else tools_dir
        tools_path = base_dir / "tools"

        if not tools_path.exists() or not tools_path.is_dir():
            logger.warning(f"Tools directory not found: {tools_path}")
            return {}

        # Get all directories in the tools directory (each should be a tool)
        tool_dirs = [d for d in tools_path.iterdir() if d.is_dir() and not d.name.startswith("__")]

        for tool_dir in tool_dirs:
            tool_name = tool_dir.name

            # Check if the required files exist
            tool_file = tool_dir / "tool.py"
            schema_file = tool_dir / "schemas.py"

            if not tool_file.exists() or not schema_file.exists():
                logger.warning(f"Tool {tool_name} is missing required files")
                continue

            try:
                # Import the tool module
                module_path = f"tools.{tool_name}.tool"
                tool_module = importlib.import_module(module_path)

                # Find the tool class (should inherit from ToolInterface)
                for name, obj in inspect.getmembers(tool_module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, ToolInterface)
                        and obj != ToolInterface
                    ):

                        # Validate that the tool has the required attributes and methods
                        self._validate_tool_class(obj, tool_name)

                        # Register the tool
                        self.tools[tool_name] = obj
                        logger.info(f"Discovered tool: {tool_name}")
                        break

            except Exception as e:
                error_msg = f"Error loading tool {tool_name}: {str(e)}"
                logger.error(error_msg)
                raise ToolDiscoveryError(error_msg) from e

        return self.tools

    def _validate_tool_class(self, tool_class: Type[ToolInterface], tool_name: str) -> List[str]:
        """
        Validate that a tool class correctly implements the ToolInterface.

        Args:
            tool_class: The tool class to validate
            tool_name: The name of the tool (for error messages)

        Returns:
            List of validation errors, empty if valid

        Raises:
            ToolDiscoveryError: If the tool class fails validation
        """
        errors = []

        # Check for required class attributes
        if not hasattr(tool_class, "name") or not tool_class.name:
            errors.append(f"Tool {tool_name} is missing 'name' class attribute")

        if not hasattr(tool_class, "description") or not tool_class.description:
            errors.append(f"Tool {tool_name} is missing 'description' class attribute")

        # Check execute method
        if not hasattr(tool_class, "execute"):
            errors.append(f"Tool {tool_name} is missing 'execute' method")
        else:
            execute_method = getattr(tool_class, "execute")
            if not inspect.iscoroutinefunction(execute_method):
                errors.append(f"Tool {tool_name} 'execute' method must be async (use 'async def')")

        # Check schema methods
        for method_name in ["get_input_schema", "get_output_schema"]:
            if not hasattr(tool_class, method_name):
                errors.append(f"Tool {tool_name} is missing '{method_name}' class method")
            else:
                method = getattr(tool_class, method_name)
                if not inspect.ismethod(method):
                    errors.append(
                        f"Tool {tool_name} '{method_name}' must be a class method (use @classmethod)"
                    )

                # Try calling the method to see if it returns a Pydantic model
                try:
                    schema = method()
                    if not inspect.isclass(schema) or not issubclass(schema, BaseModel):
                        errors.append(
                            f"Tool {tool_name} '{method_name}' must return a Pydantic model class"
                        )
                except Exception as e:
                    errors.append(f"Error calling '{method_name}' for tool {tool_name}: {str(e)}")

        if errors:
            error_msg = "\n".join(errors)
            logger.error(error_msg)
            raise ToolDiscoveryError(error_msg)

        return errors

    def register_routes(self, app: FastAPI) -> None:
        """
        Register FastAPI routes for each discovered tool.

        Args:
            app: The FastAPI application
        """
        # Get auth dependencies
        config = get_config()
        auth_dependencies = []
        auth_enabled = config.get("auth.enabled", False)

        if auth_enabled:
            try:
                from app.auth.sso import get_auth_dependencies

                auth_dependencies = get_auth_dependencies()
                logger.info(f"Using {len(auth_dependencies)} auth dependencies")
            except ImportError as exc:
                logger.error("Authentication required but dependencies not installed")
                raise ToolDiscoveryError("Authentication dependencies not installed") from exc

        # Function factories to avoid closure issues
        def create_list_tools_handler(tools_dict):
            """Create handler for listing tools."""

            # pylint: disable=unused-variable
            async def list_tools():
                """List all available tools with their descriptions."""
                return [
                    {"name": tool_cls.name, "description": tool_cls.description}
                    for tool_cls in tools_dict.values()
                ]

            return list_tools

        def create_input_schema_handler(tool_cls):
            """Create handler for input schema endpoint."""

            async def get_input_schema():
                """Get the JSON Schema for tool input."""
                return tool_cls.get_input_schema().model_json_schema()

            return get_input_schema

        def create_output_schema_handler(tool_cls):
            """Create handler for output schema endpoint."""

            async def get_output_schema():
                """Get the JSON Schema for tool output."""
                return tool_cls.get_output_schema().model_json_schema()

            return get_output_schema

        def create_tool_executor(tool_instance, input_schema_cls, is_auth_enabled):
            """Create handler for tool execution endpoint."""

            async def execute_tool(data: input_schema_cls, request: Request):
                """Execute the tool with the provided input data."""
                try:
                    # Extract token if auth is enabled
                    token = None
                    if is_auth_enabled:
                        try:
                            from app.auth.sso import extract_token_from_request

                            token = extract_token_from_request(request)
                        except Exception as e:
                            logger.error(f"Error extracting token: {str(e)}")

                    # Execute the tool with the token
                    return await tool_instance.execute(data, token=token)
                except Exception as e:
                    logger.error(f"Error executing tool {tool_instance.name}: {str(e)}")
                    raise HTTPException(status_code=500, detail=str(e))

            return execute_tool

        # Register the route to list all tools
        list_tools_handler = create_list_tools_handler(self.tools)
        self._router.get(
            "/",
            summary="List all available tools",
            operation_id="list_tools",
            dependencies=auth_dependencies,
        )(list_tools_handler)

        # Register routes for each tool
        for tool_name, tool_class in self.tools.items():
            try:
                # Get input/output schemas
                input_schema = tool_class.get_input_schema()
                output_schema = tool_class.get_output_schema()

                # Create an instance of the tool
                tool_instance = tool_class()

                # Create handlers using factory functions
                input_schema_handler = create_input_schema_handler(tool_class)
                output_schema_handler = create_output_schema_handler(tool_class)
                execute_handler = create_tool_executor(tool_instance, input_schema, auth_enabled)

                # Set unique function names to avoid route conflicts
                input_schema_handler.__name__ = f"get_{tool_name}_input_schema"
                output_schema_handler.__name__ = f"get_{tool_name}_output_schema"
                execute_handler.__name__ = f"execute_{tool_name}"

                # Register input schema endpoint
                self._router.get(
                    f"/{tool_name}/input-schema",
                    summary=f"Get input schema for {tool_class.name}",
                    operation_id=f"get_{tool_name}_input_schema",
                    dependencies=auth_dependencies,
                )(input_schema_handler)

                # Register output schema endpoint
                self._router.get(
                    f"/{tool_name}/output-schema",
                    summary=f"Get output schema for {tool_class.name}",
                    operation_id=f"get_{tool_name}_output_schema",
                    dependencies=auth_dependencies,
                )(output_schema_handler)

                # Register tool execution endpoint
                self._router.post(
                    f"/{tool_name}",
                    response_model=output_schema,
                    summary=tool_class.description,
                    operation_id=f"execute_{tool_name}",
                    dependencies=auth_dependencies,
                )(execute_handler)

                logger.info(f"Registered routes for tool: {tool_name}")

            except Exception as e:
                error_msg = f"Error registering routes for tool {tool_name}: {str(e)}"
                logger.error(error_msg)
                raise ToolDiscoveryError(error_msg) from e

        # Include the router in the FastAPI app
        app.include_router(self._router)


# Create a singleton instance for global use
_registry = None


def get_registry() -> ToolRegistry:
    """
    Get the global tool registry instance.

    Returns:
        The global ToolRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
