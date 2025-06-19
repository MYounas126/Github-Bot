# Contributing to CodeGuardian

Thank you for your interest in contributing! Please follow these guidelines to help us maintain a high-quality, consistent, and stable project.

## 🚀 Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <your-fork-url>
   cd Github\ Bot
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **(Optional) Set up a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install development tools:**
   ```sh
   pip install black isort flake8 pre-commit
   pre-commit install
   ```

## 🧑‍💻 Coding Standards

- **Formatting:**
  - Use [black](https://black.readthedocs.io/) for code formatting.
  - Use [isort](https://pycqa.github.io/isort/) for import sorting.
  - Use [flake8](https://flake8.pycqa.org/) for linting.
- **Type Hints:**
  - All public functions and methods should include type hints.
- **Docstrings:**
  - All public classes, methods, and functions must have clear docstrings describing their purpose, arguments, and return values.
- **Naming:**
  - Use `snake_case` for variables and functions, `CamelCase` for classes.
- **Testing:**
  - All new features and bug fixes must include appropriate tests.

## 🧪 Running Tests and Linting Locally

- **Run all tests:**
  ```sh
  pytest
  ```
- **Check code formatting:**
  ```sh
  black . --check
  ```
- **Sort imports:**
  ```sh
  isort . --check-only
  ```
- **Run linter:**
  ```sh
  flake8 .
  ```
- **Run all pre-commit hooks:**
  ```sh
  pre-commit run --all-files
  ```

## 📦 Submitting a Pull Request

1. Fork the repository and create your branch from `main`.
2. Ensure your code passes all tests and pre-commit checks.
3. Add or update documentation as needed.
4. Open a pull request with a clear description of your changes.

## 💬 Need Help?
If you have questions, open an issue or join the discussion in the repository.

Thank you for helping make CodeGuardian better! 