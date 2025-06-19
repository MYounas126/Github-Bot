"""
Configuration utilities for CodeGuardian bot.
"""

import os
from typing import Any, Dict

import yaml

DEFAULT_CONFIG = {
    "coverage": {"threshold": 80, "format": "cobertura"},
    "analysis": {
        "max_function_length": 50,
        "max_nesting_depth": 3,
        "max_complexity": 10,
        "max_lines": 300,
    },
    "pr_quality": {
        "require_issue_link": True,
        "require_test_summary": True,
        "min_description_length": 50,
    },
}


def load_config() -> Dict[str, Any]:
    """
    Load configuration from .codeguardian.yml or use defaults.
    Returns a dictionary with configuration values.
    """
    config = DEFAULT_CONFIG.copy()

    # Try to load from .codeguardian.yml
    config_path = os.path.join(os.getcwd(), ".codeguardian.yml")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    # Deep merge user config with defaults
                    _deep_merge(config, user_config)
        except Exception as e:
            print(f"Warning: Error loading config file: {e}")

    return config


def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> None:
    """
    Deep merge two dictionaries, updating the base dictionary.
    """
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
