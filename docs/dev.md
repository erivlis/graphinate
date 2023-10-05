# Development

## Ruff

```shell
ruff check src
```

## Test

### Standard (cobertura) XML Coverage Report

```shell
 python -m pytest tests -n auto --cov=src --cov-branch --doctest-modules --cov-report=xml --junitxml=test_results.xml
```

### HTML Coverage Report

```shell
python -m pytest tests -n auto --cov=src --cov-branch --doctest-modules --cov-report=html --junitxml=test_results.xml
```

## Docs

### test

```shell
python -m mkdocs serve
```

### build

```shell
python -m mkdocs build
```