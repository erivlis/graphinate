# Graphinate. Data to Graphs.

> [!WARNING]
> **UNDER DEVELOPMENT**
> 
> **This library is alpha-quality**

![PyPI](https://img.shields.io/pypi/v/graphinate)
![PyPI - Status](https://img.shields.io/pypi/status/graphinate)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/graphinate)
![GitHub](https://img.shields.io/github/license/erivlis/graphinate)
![PyPI - Downloads](https://img.shields.io/pypi/dd/graphinate)
![GitHub repo size](https://img.shields.io/github/repo-size/erivlis/graphinate)
[![Contributors](https://img.shields.io/github/contributors/erivlis/graphinate.svg)](https://github.com/erivlis/graphinate/graphs/contributors)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/erivlis/graphinate)

[![Tests](https://github.com/erivlis/graphinate/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/erivlis/graphinate/actions/workflows/test.yml)
[![Publish](https://github.com/erivlis/graphinate/actions/workflows/publish.yml/badge.svg)](https://github.com/erivlis/graphinate/actions/workflows/publish.yml)

## Introduction

### What is Graphinate?

Graphinate is a library that aims to simplify the generation of Graph Data Structures from Data Sources.

It utilizes and builds upon the excellent [**_NetworkX_**](https://networkx.org/) library.

In addition, it has several interfaces for ease of use:

- CLI (using [**_Click_**](https://palletsprojects.com/p/click/)),
- GraphQL API (using [**_Strawberry GraphQL_**](https://strawberry.rocks/)).

[//]: # (- TUI &#40;using [**_Textual_**]&#40;https://textual.textualize.io/&#41;&#41; **⚠️Not available yet⚠️**)

## Install

Graphinate is available on PyPI:

```shell
pip install graphinate
```

To install with server support

```shell
pip install graphinate[server]
```

Graphinate officially supports Python 3.9+.

## Quick Start

### `GraphModel`

Graphinate defines the `GraphModel` Class which can be used to declaratively register _Edge_ and/or _Node_ data
supplier functions by using decorators.

### `materialize`

Graphinate supplies a `materialize` function to output the `GraphModel`.

### Example

```python
import graphinate

N: int = 8

# Define GraphModel
graph_model = graphinate.GraphModel(name="Octagonal Graph")


# Register edges supplier function
@graph_model.edge()
def edge():
    for i in range(N):
        yield {'source': i, 'target': i + 1}
    yield {'source': N, 'target': 0}


# Materialize the GraphModel
graphinate.materialize(graph_model)
```

## CLI

### Commands

```
Usage: python -m graphinate [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  save
  server
```

#### Save

```
Usage: python -m graphinate save [OPTIONS] MODEL

Options:
  --help  Show this message and exit.
```

#### Server

```
Usage: python -m graphinate server [OPTIONS] MODEL

Options:
  -p, --port INTEGER
  --help              Show this message and exit.
```

## TUI

UNDER DEVELOPMENT

## Gallery

### Python AST

![d3_graph_ast](https://github.com/erivlis/graphinate/assets/9897520/9e7e1ed2-3a5c-41fe-8c5f-999da4b741ff)

### GitHub Repository

![repo_graph](https://github.com/erivlis/graphinate/assets/9897520/9c044bbe-1f21-41b8-b879-95b8362ad48d)

### Python AST - 3D Force-Directed Animation

![AST 3D Force animation](https://github.com/erivlis/graphinate/assets/9897520/2e9a53b1-5686-4683-a0e4-fbffa850a27b)

## Development

### Lint

```shell
ruff check src
```

### Docs

```shell
python -m mkdocs build
```

### Build

```shell
python -m build
```

### Test

```shell
 python -m pytest ./tests --cov=./src --cov-branch --cov-report=xml --junitxml=test_results.xml
```

## Acknowledgements

### Dependencies

#### Python

<a href="https://palletsprojects.com/p/click/"><img height="50" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://click.palletsprojects.com/en/7.x/_images/click-logo.png" alt="Click Logo."></a>
<a href="https://github.com/Delgan/loguru"><img height="50" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://raw.githubusercontent.com/Delgan/loguru/master/docs/_static/img/logo.png" alt="Loguru Logo."></a>
<a href="https://matplotlib.org/"><img height="50" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://matplotlib.org/_static/logo_dark.svg" alt="matplotlib Logo."></a>
<a href="https://networkx.org/"><img height="50" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://networkx.org/_static/networkx_logo.svg" alt="NetworkX Logo."></a>
<a href="https://strawberry.rocks/"><img height="50" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://github.com/strawberry-graphql/strawberry/raw/main/.github/logo.png" alt="Strawberry GraphQL Logo."></a>

#### Javascript and HTML

<a href="https://vasturiano.github.io/3d-force-graph/"><img height="50" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="http://gist.github.com/vasturiano/02affe306ce445e423f992faeea13521/raw/preview.png" alt="3D Force-Directed Graph Logo."></a>
<a href="https://github.com/graphql-kit/graphql-voyager"><img height="50" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://github.com/graphql-kit/graphql-voyager/raw/main/docs/cover.png" alt="Graphql Voyager Logo."></a>

### Dev Tools

<a href="https://hatch.pypa.io/"><img height="50" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://hatch.pypa.io/latest/assets/images/logo.svg" alt="Hatch logo."></a>
<a href="https://pytest.org"><img height="50" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://docs.pytest.org/en/7.4.x/_static/pytest_logo_curves.svg" alt="pytest logo."></a>
<a href="https://astral.sh/ruff"><img height="50" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://astralcms.wpengine.com/wp-content/uploads/2023/03/Ruff-Logo.svg" alt="Ruff logo."></a>

### IDE

<a href="https://www.jetbrains.com/pycharm/"><img height="50" style="background: linear-gradient(-45deg, #FCF84A, #3DEA62, #21D789);" src="https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.png" alt="PyCharm logo."></a>