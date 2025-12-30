# Development

This guide provides instructions for setting up your development environment to contribute to Graphinate.

## Install dependencies

UV is used to install all dependencies, including those for testing and documentation.

```shell
uv sync --all-extras --all-groups
```

## Update dependencies

To update the locked dependencies to their latest versions:

```shell
uv lock --upgrade
uv sync --all-extras --all-groups
```

## Ruff

[Ruff](https://github.com/astral-sh/ruff) is used for linting and formatting.

### Report issues

=== "src"

    ```shell
    ruff check src
    ```

=== "tests"

    ```shell
    ruff check tests
    ```

### Fix issues

=== "src"

    ```shell
    ruff check src --fix
    ```

=== "tests"

    ```shell
    ruff check tests --fix
    ```

## Test

We use [pytest](https://pytest.org) for testing.

=== "Terminal"

    > This is the recommended command for local development, as it provides the fastest feedback.

    ```shell
    python -m pytest tests --cov=src --cov-branch --doctest-modules --cov-report=term --junitxml=junit.xml
    ```

=== "HTML"

    > Generates an interactive HTML coverage report.

    ```shell
    python -m pytest tests --cov=src --cov-branch --doctest-modules --cov-report=html --junitxml=junit.xml
    ```

=== "XML"

    > Generates a standard Cobertura XML report (useful for CI/CD).

    ```shell
    python -m pytest tests --cov=src --cov-branch --doctest-modules --cov-report=xml --junitxml=junit.xml
    ```

## Docs

The documentation is built using [MkDocs](https://www.mkdocs.org/) with
the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.

### Test

To serve the documentation locally for testing:

```shell
python -m mkdocs serve
```

### Build

To build the static documentation site:

```shell
python -m mkdocs build
```
