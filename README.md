# Graphinate. Data to Graphs.

## ⚠️ **Under Development!** ⚠️

This library is alpha-quality

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

## Install

Graphinate is available on PyPI:

```shell
python -m pip install graphinate 
```

Graphinate officially supports Python 3.9+.

## Introduction

### What is Graphinate?

Graphinate aims to simplify the generation of Graph data structures from sources of data.
It utilizes and build upon [NetworkX](https://networkx.org/)

### What is a Graph?

> In a mathematician's terminology, a graph is a collection of points and lines connecting some (possibly empty) subset
> of them. The points of a graph are most commonly known as graph vertices, but may also be called "nodes" or simply "
> points." Similarly, the lines connecting the vertices of a graph are most commonly known as graph edges, but may also
> be
> called "arcs" or "lines."
>
> &mdash; [https://mathworld.wolfram.com/Graph.html](https://mathworld.wolfram.com/Graph.html)

### What is Data?

> ...data is a collection of discrete or continuous values that convey information, describing the quantity, quality,
> fact, statistics, other basic units of meaning, or simply sequences of symbols that may be further interpreted
> formally.
>
> &mdash; [https://en.wikipedia.org/wiki/Data](https://en.wikipedia.org/wiki/Data)

### Defining a Graph

One can define Graphs in two general ways:

#### Edge first

Generate a Graph by supplying a list of edges. The simplest definition of an edge will be a tuple of 2 values. Each
value represent a node (or vertex) in the graph. Additional attributes may be also added to the edge definition to
signify additional meaning.

In this case one defines the **edges explicitly** and the **nodes implicitly**.

Such graph is focused more on the _relationships_ or the _structure_ of the Graph than on the nodes themselves.

#### Node first

Alternatively, one can first add nodes (vertices) to a graph without defining edges. Additional attributes may be added
to the node definition to signify additional meaning. Later on edge definitions are added to generate the relationships
between the nodes.

In this case **both nodes and the edges** are defines **explicitly**.

Such a graph has focus first on the nodes and later on the relationship between them.

## Gallery

![d3_graph_ast](https://github.com/erivlis/graphinate/assets/9897520/9e7e1ed2-3a5c-41fe-8c5f-999da4b741ff)
![repo_graph](https://github.com/erivlis/graphinate/assets/9897520/9c044bbe-1f21-41b8-b879-95b8362ad48d)
![AST 3D Force animation](https://github.com/erivlis/graphinate/assets/9897520/2e9a53b1-5686-4683-a0e4-fbffa850a27b)

## Examples

- [ ] Code
  - [ ] Call Graph
  - [x] Python AST
- [x] GitHub
  - [x] Repository
  - [x] Followers
- [ ] Ethernet
  - [ ] Traceroute
- [ ] Math
  - [x] Graph Atlas
  - [ ] Hailstone
- [ ] Text
  - [ ] NLP
- [ ] Web
  - [ ] Web Graph

## Guide

### By Convention

https://github.com/erivlis/graphinate/blob/f5b363a360907aecf52cf11249b78666eb470d20/examples/github/followers.py#L1

### By Configuration

https://github.com/erivlis/graphinate/blob/f5b363a360907aecf52cf11249b78666eb470d20/examples/github/repositories.py#L1

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

<a href="https://vasturiano.github.io/3d-force-graph/"><img height="50" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="http://gist.github.com/vasturiano/02affe306ce445e423f992faeea13521/raw/preview.png" alt="3D Force-Directed Graph Logo."></a>
<a href="https://palletsprojects.com/p/click/"><img height="50" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://click.palletsprojects.com/en/7.x/_images/click-logo.png" alt="Click Logo."></a>
<a href="https://github.com/Delgan/loguru"><img height="50" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://raw.githubusercontent.com/Delgan/loguru/master/docs/_static/img/logo.png" alt="Loguru Logo."></a>
<a href="https://matplotlib.org/"><img height="50" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://matplotlib.org/_static/logo_dark.svg" alt="matplotlib Logo."></a>
<a href="https://networkx.org/"><img height="50" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://networkx.org/_static/networkx_logo.svg" alt="NetworkX Logo."></a>
<a href="https://strawberry.rocks/"><img height="50" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://github.com/strawberry-graphql/strawberry/raw/main/.github/logo.png" alt="Strawberry GraphQL Logo."></a>

### Dev Tools

<a href="https://hatch.pypa.io/"><img height="50" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://hatch.pypa.io/latest/assets/images/logo.svg" alt="Hatch logo."></a>
<a href="https://pytest.org"><img height="50" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://docs.pytest.org/en/7.4.x/_static/pytest_logo_curves.svg" alt="pytest logo."></a>
<a href="https://astral.sh/ruff"><img height="50" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://astralcms.wpengine.com/wp-content/uploads/2023/03/Ruff-Logo.svg" alt="Ruff logo."></a>

### IDE

<a href="https://www.jetbrains.com/pycharm/"><img height="50" style="background: linear-gradient(-45deg, #FCF84A, #3DEA62, #21D789);" src="https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.png" alt="PyCharm logo."></a>