"""
Configuration management for the application.

This module handles loading, merging, and accessing configuration from various sources:
- Default values
- Configuration files (TOML)
- Environment variables
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache
import tomli


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""


class Config:
    """
    Configuration manager that handles loading and merging configuration.
    """

    def __init__(self, root_dir: Path = None):
        """
        Initialize the configuration manager.

        Args:
            root_dir: The root directory of the project, used to locate config files
        """
        self.root_dir = root_dir or Path.cwd()
        self._config: Dict[str, Any] = {}
        self._loaded = False

    def load(self) -> None:
        """
        Load configuration from all sources.

        The configuration is loaded in this order, with later sources overriding earlier ones:
        1. Default values
        2. Root config file
        3. Environment variables
        """
        self._config = self._get_default_config()
        # Load from root config file
        root_config = self._load_toml_file(self.root_dir / "config.toml")
        if root_config:
            self._merge_config(self._config, root_config)

        # Load from environment variables
        env_config = self._load_from_environment()
        if env_config:
            self._merge_config(self._config, env_config)

        self._loaded = True

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: The configuration key, can use dot notation for nested values
            default: Default value if the key is not found

        Returns:
            The configuration value, or the default if not found
        """
        if not self._loaded:
            self.load()

        parts = key.split(".")
        value = self._config

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value

    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific tool.

        Args:
            tool_name: The name of the tool

        Returns:
            The tool's configuration, merged with global defaults
        """
        if not self._loaded:
            self.load()

        # Start with global tool defaults
        tool_config = self.get("tools.defaults", {}).copy()

        # Load tool-specific config file
        tool_dir = self.root_dir / "tools" / tool_name
        tool_config_file = tool_dir / "config.toml"

        if tool_config_file.exists():
            try:
                with open(tool_config_file, "rb") as f:
                    local_config = tomli.load(f)
                # Merge with defaults
                self._merge_config(tool_config, local_config)
            except Exception as e:
                raise ConfigurationError(f"Error loading tool config for {tool_name}: {str(e)}")

        return tool_config

    def _get_default_config(self) -> Dict[str, Any]:
        """Get the default configuration values."""
        return {
            "app": {
                "name": "llm",
                "description": "picture story generation",
                "version": "0.1.0",
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "reload": False,
                
                "docker": True,
                
            },
            "auth": {
                
                "enabled": False,
                
                "provider": "sso",
            },
            "llm": {
                
                "enabled": True,
                "provider": "ollama",
                
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "model": "llama3",
                },
                
                
            },
            "tools": {
                "defaults": {},
                
                "sample_tool": {
                    "timeout": 30,
                }
                
            },
        }

    def _load_toml_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load configuration from a TOML file.

        Args:
            file_path: Path to the TOML file

        Returns:
            The loaded configuration, or None if the file doesn't exist
        """
        if not file_path.exists():
            return None

        try:
            with open(file_path, "rb") as f:
                return tomli.load(f)
        except Exception as e:
            raise ConfigurationError(f"Error loading config file {file_path}: {str(e)}")

    def _load_from_environment(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables.

        Environment variables that start with "APP_" are converted to configuration keys:
        - APP_SERVER_PORT=8080 -> server.port=8080
        - APP_AUTH_ENABLED=true -> auth.enabled=True

        Returns:
            Configuration dictionary based on environment variables
        """
        result = {}
        prefix = "APP_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and split into parts
                config_key = key[len(prefix) :].lower()
                parts = config_key.split("_")

                if value.lower() in ("true", "yes", "1"):
                    typed_value = True
                elif value.lower() in ("false", "no", "0"):
                    typed_value = False
                elif value.isdigit():
                    typed_value = int(value)
                elif value.replace(".", "", 1).isdigit():
                    typed_value = float(value)
                else:
                    typed_value = value

                # Build nested dictionary
                current = result
                for i, part in enumerate(parts):
                    if i == len(parts) - 1:
                        current[part] = typed_value
                    else:
                        if part not in current:
                            current[part] = {}
                        current = current[part]

        return result

    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively merge source configuration into target.

        Args:
            target: The target configuration dictionary
            source: The source configuration dictionary
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value


@lru_cache()
def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        The global Config instance
    """
    return Config()
