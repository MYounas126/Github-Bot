import re
from typing import Any, Dict, List

from codeguardian.analyzers.base import BaseAnalyzer


class DocumentationAnalyzer(BaseAnalyzer):
    """Documentation analyzer plugin that checks code documentation quality."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the documentation analyzer.

        Args:
            config: Configuration dictionary with documentation settings
        """
        super().__init__(config)
        self.require_readme = config.get("require_readme", True)
        self.require_api_docs = config.get("require_api_docs", True)
        self.min_doc_coverage = config.get("min_doc_coverage", 80)

        # Documentation patterns
        self.patterns = {
            "function": re.compile(r"def\s+(\w+)\s*\("),
            "class": re.compile(r"class\s+(\w+)"),
            "module": re.compile(r'"""([^"]*)"""', re.DOTALL),
        }

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code documentation quality.

        Args:
            context: Analysis context containing file contents and metadata

        Returns:
            Dictionary containing documentation analysis results
        """
        if not self.enabled:
            return {}

        results = {
            "status": "success",
            "issues": [],
            "metrics": {"doc_coverage": 0, "total_items": 0, "documented_items": 0},
        }

        # Check for README
        if self.require_readme:
            has_readme = any(
                file_info.get("path", "").lower() in ["readme.md", "readme.rst"]
                for file_info in context.get("files", [])
            )
            if not has_readme:
                results["issues"].append(
                    {
                        "type": "missing_readme",
                        "severity": "high",
                        "message": "README file is required but not found",
                    }
                )

        # Analyze each file
        for file_info in context.get("files", []):
            content = file_info.get("content", "")
            path = file_info.get("path", "")

            # Skip non-Python files
            if not path.endswith(".py"):
                continue

            # Count documented items
            total_items = 0
            documented_items = 0

            # Check module docstring
            module_doc = self.patterns["module"].search(content)
            if not module_doc:
                results["issues"].append(
                    {
                        "type": "missing_module_doc",
                        "file": path,
                        "severity": "medium",
                        "message": "Module is missing docstring",
                    }
                )
            else:
                documented_items += 1
            total_items += 1

            # Check class documentation
            for class_match in self.patterns["class"].finditer(content):
                class_name = class_match.group(1)
                class_start = class_match.start()

                # Look for class docstring
                class_doc = self.patterns["module"].search(content[class_start:])
                if not class_doc:
                    results["issues"].append(
                        {
                            "type": "missing_class_doc",
                            "file": path,
                            "line": content[:class_start].count("\n") + 1,
                            "severity": "medium",
                            "message": f"Class '{class_name}' is missing docstring",
                        }
                    )
                else:
                    documented_items += 1
                total_items += 1

            # Check function documentation
            for func_match in self.patterns["function"].finditer(content):
                func_name = func_match.group(1)
                func_start = func_match.start()

                # Look for function docstring
                func_doc = self.patterns["module"].search(content[func_start:])
                if not func_doc:
                    results["issues"].append(
                        {
                            "type": "missing_function_doc",
                            "file": path,
                            "line": content[:func_start].count("\n") + 1,
                            "severity": "medium",
                            "message": f"Function '{func_name}' is missing docstring",
                        }
                    )
                else:
                    documented_items += 1
                total_items += 1

            # Update metrics
            results["metrics"]["total_items"] += total_items
            results["metrics"]["documented_items"] += documented_items

        # Calculate documentation coverage
        if results["metrics"]["total_items"] > 0:
            results["metrics"]["doc_coverage"] = (
                results["metrics"]["documented_items"]
                / results["metrics"]["total_items"]
                * 100
            )

            # Check coverage threshold
            if results["metrics"]["doc_coverage"] < self.min_doc_coverage:
                results["issues"].append(
                    {
                        "type": "low_doc_coverage",
                        "severity": "medium",
                        "message": f"Documentation coverage ({results['metrics']['doc_coverage']:.1f}%) "
                        f"is below threshold ({self.min_doc_coverage}%)",
                    }
                )

        # Add recommendations
        if results["issues"]:
            results["recommendations"] = [
                "Add docstrings to all modules, classes, and functions",
                "Include type hints in function signatures",
                "Document parameters and return values",
                "Add examples in docstrings where appropriate",
            ]

        return results
