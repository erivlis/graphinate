# Style Guide

This document outlines the coding, testing, and documentation style guidelines for the Graphinate project. These
guidelines are meant to complement established standards like PEP 8.

## Linting and Formatting

To maintain a consistent codebase, we use the following tools for linting and formatting:

* **`ruff`**: For linting and formatting Python code. The configuration is defined in `pyproject.toml`. It's recommended
  to integrate `ruff` into your IDE to get real-time feedback.
* **`mdformat`**: For formatting Markdown files, including documentation. This ensures a consistent style across all our
  documentation.

## Code Style

* **Line Length**: Maximum 120 characters.
* **Quotes** - use the following rulea unless there's a good reason not to:
    * Use single quotes for strings.
    * Use double quotes for docstrings.
    * Use double quotes for f-strings.
* **Type Hinting**: All function and method signatures should include type hints.
* **Docstrings**: All public modules, functions, classes, and methods should have a docstring. We follow
  the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for
  docstring format.
* **Logging**: Use the `loguru` library for all logging.
* **Complexity**: Aim to keep the cyclomatic complexity of functions at or below 15, as configured in `ruff`.

## Test Style

Tests are written using the `pytest` framework.

* **Location**: All tests reside in the `tests/` directory.
* **Naming**: Test files must be named `test_*.py`, and test functions must be prefixed with `test_`.
* **Structure**: Tests should follow the "Arrange, Act, Assert" pattern to ensure clarity and separation of concerns.
* **Fixtures**: Use `pytest` fixtures for setup and teardown logic. Place common fixtures in `tests/conftest.py`.
* **Mocks**: Use the `pytest-mock` library for mocking dependencies.

## Documentation Style

Project documentation is generated using `mkdocs` with the `mkdocs-material` theme.

* **Format**: All documentation is written in Markdown and formatted with `mdformat`.
* **Admonitions**: Use admonitions to highlight specific information. For example:
  ```markdown
  !!! note
      This is a note.
  ```
* **Code Blocks**: Use fenced code blocks with language identifiers for all code examples.
  ```python
  def my_function():
      print("Hello, world!")
  ```
* **Tables**: Use standard Markdown tables for presenting tabular data.
* **Internal Linking**: Use relative paths when linking to other internal documentation pages.

## Git and Commit Style

To maintain a clean and understandable version history, we follow these Git practices:

* **Commit Messages**: We adhere to the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
  specification. This helps in automating changelog generation and makes the commit history more readable. Each commit
  message should have a type (e.g., `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`) and a concise
  description.

  Example:
  ```
  feat: add user authentication service
  ```

* **Branching**: Create new branches for each feature or bug fix. Name branches descriptively, like `feat/add-auth` or
  `fix/login-bug`.

* **Clean History**: Aim for a clean, linear history. Before merging a feature branch, rebase it on top of the main
  branch and squash related commits into logical units. Avoid merge commits for small features.
