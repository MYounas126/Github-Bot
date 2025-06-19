from typing import Any, Dict


class BaseAnalyzer:
    """Base class for all analyzers."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the analyzer.

        Args:
            config: Configuration dictionary
        """
        self.enabled = config.get("enabled", True)
        self.config = config

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the given context.

        Args:
            context: Analysis context containing file contents and metadata

        Returns:
            Dictionary containing analysis results
        """
        if not self.enabled:
            return {}

        raise NotImplementedError("Subclasses must implement analyze()")
