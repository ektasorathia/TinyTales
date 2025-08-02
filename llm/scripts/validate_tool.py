"""
Tool validation script.

This script validates that all tools in the tools directory follow the required structure.
"""

import importlib
import inspect
from pathlib import Path
import sys

from loguru import logger

# Add the project root to the path using the script's location
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from app.core.interfaces import ToolInterface
from pydantic import BaseModel


def validate_tool(tool_dir: Path) -> bool:
    """
    Validate a single tool.

    Args:
        tool_dir: Path to the tool directory

    Returns:
        bool: True if the tool is valid, False otherwise
    """
    tool_name = tool_dir.name
    logger.info(f"Validating tool: {tool_name}")

    # Check required files
    required_files = ["tool.py", "schemas.py"]
    missing_files = []

    for file in required_files:
        if not (tool_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False

    # Check if the tool can be imported
    try:
        module_path = f"tools.{tool_name}.tool"
        tool_module = importlib.import_module(module_path)

        # Find the tool class
        tool_class = None
        for name, obj in inspect.getmembers(tool_module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, ToolInterface)
                and obj != ToolInterface
                and obj.__module__ == module_path
            ):
                tool_class = obj
                break

        if tool_class is None:
            logger.error(f"No class found in {tool_name}/tool.py that inherits from ToolInterface")
            return False

        # Check required attributes
        if not hasattr(tool_class, "name") or not tool_class.name:
            logger.error("Tool class missing or empty 'name' class attribute")
            return False

        if not hasattr(tool_class, "description") or not tool_class.description:
            logger.error("Tool class missing or empty 'description' class attribute")
            return False

        errors = []

        # Check execute method
        if not hasattr(tool_class, "execute"):
            errors.append("Missing 'execute' method")
        else:
            execute_method = getattr(tool_class, "execute")
            if not inspect.iscoroutinefunction(execute_method):
                errors.append("'execute' method must be async (use 'async def')")

        # Check schema methods
        for method_name in ["get_input_schema", "get_output_schema"]:
            if not hasattr(tool_class, method_name):
                errors.append(f"Missing '{method_name}' class method")
            else:
                method = getattr(tool_class, method_name)
                if not inspect.ismethod(method):
                    errors.append(f"'{method_name}' must be a class method (use @classmethod)")

                # Try calling the method to see if it returns a Pydantic model
                try:
                    schema = method()
                    if not inspect.isclass(schema) or not issubclass(schema, BaseModel):
                        errors.append(f"'{method_name}' must return a Pydantic model class")
                except Exception as e:
                    errors.append(f"Error calling '{method_name}': {str(e)}")

        if errors:
            for error in errors:
                logger.error(f"Tool class validation error: {error}")
            return False

        # Validate schemas
        try:
            schema_module = importlib.import_module(f"tools.{tool_name}.schemas")

            # Check for InputSchema
            if not hasattr(schema_module, "InputSchema"):
                logger.error("Missing InputSchema in schemas.py")
                return False

            # Check for OutputSchema
            if not hasattr(schema_module, "OutputSchema"):
                logger.error("Missing OutputSchema in schemas.py")
                return False

            # Check that InputSchema and OutputSchema are Pydantic models
            if not issubclass(schema_module.InputSchema, BaseModel):
                logger.error("InputSchema is not a Pydantic BaseModel")
                return False

            if not issubclass(schema_module.OutputSchema, BaseModel):
                logger.error("OutputSchema is not a Pydantic BaseModel")
                return False

        except Exception as e:
            logger.error(f"Error validating schemas: {str(e)}")
            return False

        logger.info(f"SUCCESS: Tool '{tool_name}' is valid")
        return True

    except Exception as e:
        logger.error(f"Exception during validation: {str(e)}")
        return False


def validate_all_tools() -> bool:
    """
    Validate all tools in the tools directory.

    Returns:
        bool: True if all tools are valid, False otherwise
    """
    tools_dir = Path.cwd() / "tools"

    if not tools_dir.exists() or not tools_dir.is_dir():
        logger.error("Tools directory not found")
        return False

    tool_dirs = [d for d in tools_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]

    if not tool_dirs:
        logger.warning("No tools found in the tools directory")
        return True

    valid = True
    for tool_dir in tool_dirs:
        if not validate_tool(tool_dir):
            valid = False

    return valid


if __name__ == "__main__":
    print("Validating tools...")
    if validate_all_tools():
        print("\nAll tools are valid!")
        sys.exit(0)
    else:
        print("\nTool validation failed. Please fix the issues above.")
        sys.exit(1)
