# CodeGuardian 🤖

[![PyPI version](https://badge.fury.io/py/codeguardian.svg)](https://badge.fury.io/py/codeguardian)
[![Python Versions](https://img.shields.io/pypi/pyversions/codeguardian.svg)](https://pypi.org/project/codeguardian/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/MYounas126/Github-Bot/actions/workflows/ci.yml/badge.svg)](https://github.com/MYounas126/Github-Bot/actions/workflows/ci.yml)

A GitHub bot for automated code quality and documentation analysis. CodeGuardian helps maintain high code quality standards by analyzing pull requests for:

- 📝 Documentation coverage
- 🧪 Test coverage
- 🎯 Code quality metrics
- 📊 PR quality metrics

## 🚀 Quick Start

### As a GitHub Action

1. Create `.github/workflows/codeguardian.yml` in your repository:

```yaml
name: CodeGuardian

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install CodeGuardian
        run: |
          python -m pip install --upgrade pip
          pip install codeguardian
          
      - name: Run CodeGuardian
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python -m codeguardian.main
```

### As a Python Package

```bash
pip install codeguardian
```

### Using Docker

```bash
docker build -t myounas126/codeguardian .
docker run -e GITHUB_TOKEN=your_token myounas126/codeguardian
```

## ⚙️ Configuration

Create a `.codeguardian.yml` file in your repository root:

```yaml
documentation:
  require_readme: true
  require_api_docs: true
  min_doc_coverage: 80

code_quality:
  max_complexity: 10
  min_maintainability: 50

pr_quality:
  min_description_length: 50
  require_test_mention: true
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub API token | Required |
| `CACHE_DIR` | Cache directory | `.cache` |
| `CACHE_TTL` | Cache TTL in seconds | `3600` |
| `MAX_RETRIES` | Max API retry attempts | `3` |
| `BASE_DELAY` | Base retry delay in seconds | `1.0` |
| `MAX_DELAY` | Max retry delay in seconds | `30.0` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 📚 Documentation

For detailed documentation, visit our [documentation site](https://github.com/MYounas126/Github-Bot#readme).

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 