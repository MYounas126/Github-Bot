import pytest

from codeguardian.plugins.documentation.analyzer import DocumentationAnalyzer


@pytest.fixture
def analyzer():
    """Create a documentation analyzer instance."""
    return DocumentationAnalyzer(
        {"require_readme": True, "require_api_docs": True, "min_doc_coverage": 80}
    )


def test_documentation_analyzer_initialization(analyzer):
    """Test documentation analyzer initialization."""
    assert analyzer.enabled
    assert analyzer.require_readme
    assert analyzer.require_api_docs
    assert analyzer.min_doc_coverage == 80


def test_documentation_analyzer_disabled():
    """Test documentation analyzer when disabled."""
    analyzer = DocumentationAnalyzer({"enabled": False})
    results = analyzer.analyze({"files": []})
    assert results == {}


def test_documentation_analyzer_missing_readme(analyzer):
    """Test detection of missing README."""
    context = {"files": [{"path": "main.py", "content": "def hello(): pass"}]}

    results = analyzer.analyze(context)

    assert results["status"] == "success"
    assert len(results["issues"]) > 0
    assert any(issue["type"] == "missing_readme" for issue in results["issues"])


def test_documentation_analyzer_missing_docstrings(analyzer):
    """Test detection of missing docstrings."""
    context = {
        "files": [
            {
                "path": "main.py",
                "content": """
                def hello():
                    pass
                
                class MyClass:
                    def __init__(self):
                        pass
                """,
            }
        ]
    }

    results = analyzer.analyze(context)

    assert results["status"] == "success"
    assert len(results["issues"]) > 0
    assert any(issue["type"] == "missing_module_doc" for issue in results["issues"])
    assert any(issue["type"] == "missing_class_doc" for issue in results["issues"])
    assert any(issue["type"] == "missing_function_doc" for issue in results["issues"])


def test_documentation_analyzer_doc_coverage(analyzer):
    """Test documentation coverage calculation."""
    context = {
        "files": [
            {
                "path": "main.py",
                "content": '''
                """Module docstring."""
                
                def hello():
                    """Function docstring."""
                    pass
                
                class MyClass:
                    """Class docstring."""
                    def __init__(self):
                        pass
                ''',
            }
        ]
    }

    results = analyzer.analyze(context)

    assert results["status"] == "success"
    assert results["metrics"]["doc_coverage"] == 75.0  # 3 out of 4 items documented
    assert any(issue["type"] == "low_doc_coverage" for issue in results["issues"])


def test_documentation_analyzer_good_coverage():
    """Test with good documentation coverage."""
    analyzer = DocumentationAnalyzer({"min_doc_coverage": 50})
    context = {
        "files": [
            {
                "path": "main.py",
                "content": '''
                """Module docstring."""
                
                def hello():
                    """Function docstring."""
                    pass
                ''',
            }
        ]
    }

    results = analyzer.analyze(context)

    assert results["status"] == "success"
    assert results["metrics"]["doc_coverage"] == 100.0
    assert not any(issue["type"] == "low_doc_coverage" for issue in results["issues"])


def test_documentation_analyzer_recommendations(analyzer):
    """Test generation of documentation recommendations."""
    context = {
        "files": [
            {
                "path": "main.py",
                "content": """
                def hello():
                    pass
                """,
            }
        ]
    }

    results = analyzer.analyze(context)

    assert results["status"] == "success"
    assert "recommendations" in results
    assert len(results["recommendations"]) > 0
    assert (
        "Add docstrings to all modules, classes, and functions"
        in results["recommendations"]
    )


def test_documentation_analyzer_multiple_files(analyzer):
    """Test analysis of multiple files."""
    context = {
        "files": [
            {"path": "module1.py", "content": "def func1(): pass"},
            {
                "path": "module2.py",
                "content": '"""Module docstring."""\ndef func2(): pass',
            },
        ]
    }

    results = analyzer.analyze(context)

    assert results["status"] == "success"
    assert results["metrics"]["total_items"] == 4  # 2 modules + 2 functions
    assert results["metrics"]["documented_items"] == 1  # Only module2 is documented


def test_documentation_analyzer_non_python_files(analyzer):
    """Test analysis with non-Python files."""
    context = {
        "files": [
            {"path": "data.json", "content": '{"key": "value"}'},
            {"path": "README.md", "content": "# Project Documentation"},
        ]
    }

    results = analyzer.analyze(context)

    assert results["status"] == "success"
    assert results["metrics"]["total_items"] == 0  # No Python files to analyze
    assert not any(issue["type"] == "missing_readme" for issue in results["issues"])
