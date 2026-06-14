```markdown
# iphoneprice Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the `iphoneprice` Python repository. It covers file and code organization, import/export styles, commit patterns, and testing approaches. While no specific framework is used, the repository follows Pythonic best practices for modularity and maintainability.

## Coding Conventions

### File Naming
- Use **snake_case** for all Python file names.
  - Example: `price_fetcher.py`, `data_parser.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import parse_price
    ```

### Export Style
- Use **named exports** (explicitly define what is exported).
  - Example:
    ```python
    def get_iphone_price(model):
        # implementation

    __all__ = ["get_iphone_price"]
    ```

### Commit Patterns
- Commit messages are **freeform** and do not follow a strict prefix.
- Average commit message length is about 36 characters.
  - Example: `add price parser for new models`

## Workflows

### Adding a New Price Fetcher
**Trigger:** When supporting a new iPhone model or data source  
**Command:** `/add-price-fetcher`

1. Create a new Python file using snake_case (e.g., `new_model_fetcher.py`).
2. Implement the fetcher logic.
3. Use relative imports to reuse utilities or parsers.
4. Export the main function using named exports.
5. Write a corresponding test file named `new_model_fetcher.test.py`.
6. Commit your changes with a descriptive message.

### Running Tests
**Trigger:** Before merging or deploying changes  
**Command:** `/run-tests`

1. Identify all test files matching the `*.test.*` pattern.
2. Run each test file using your preferred Python test runner (e.g., `pytest` or `unittest`).
   - Example:
     ```bash
     python -m unittest discover -s . -p "*.test.py"
     ```
3. Review test outputs and fix any failures.

## Testing Patterns

- Test files follow the pattern: `*.test.*` (e.g., `price_fetcher.test.py`)
- The testing framework is **unknown**; use standard Python test runners.
- Each test file should import the module under test using relative imports.
  - Example:
    ```python
    from .price_fetcher import get_iphone_price

    def test_get_iphone_price():
        assert get_iphone_price("iPhone 14") > 0
    ```

## Commands
| Command             | Purpose                                  |
|---------------------|------------------------------------------|
| /add-price-fetcher  | Scaffold and add a new price fetcher     |
| /run-tests          | Run all test files in the repository     |
```
