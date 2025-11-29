# Development

This guide provides instructions for setting up your development environment to contribute to Graphinate.

## Install dependencies

Use UV to install all dependencies, including those for testing and documentation.

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

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

### Report issues

```shell
ruff check src
```

### Fix issues

```shell
ruff check src --fix
```

## Test

We use [pytest](https://pytest.org) for testing.

### Standard (cobertura) XML Coverage Report

```shell
python -m pytest tests --cov=src --cov-branch --doctest-modules --cov-report=xml --junitxml=junit.xml
```

### HTML Coverage Report

```shell
python -m pytest tests --cov=src --cov-branch --doctest-modules --cov-report=html --junitxml=junit.xml
```

### Terminal Coverage Report

This is the recommended command for local development, as it provides the fastest feedback.

```shell
python -m pytest tests --cov=src --cov-branch --doctest-modules --cov-report=term --junitxml=junit.xml
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
