# [Graphinate. Data to Graphs.](https://erivlis.github.io/graphinate/)

<table>
  <tr style="vertical-align: middle;">
    <td rowspan="4"><img height="240" src="https://github.com/erivlis/graphinate/assets/9897520/dae41f9f-69e5-4eb5-a488-87ce7f51fa32" alt="Graphinate. Data to Graphs."></td>
    <td>Package</td>
    <td>
      <img alt="PyPI - version" src="https://img.shields.io/pypi/v/graphinate">
      <img alt="PyPI - Status" src="https://img.shields.io/pypi/status/graphinate">
      <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/graphinate">
      <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dd/graphinate">
      <br>
      <img alt="GitHub" src="https://img.shields.io/github/license/erivlis/graphinate">
      <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/erivlis/graphinate">
      <img alt="GitHub last commit (by committer)" src="https://img.shields.io/github/last-commit/erivlis/graphinate">
      <a href="https://github.com/erivlis/graphinate/graphs/contributors"><img alt="Contributors" src="https://img.shields.io/github/contributors/erivlis/graphinate.svg"></a>
 	    <img alt="GitHub Watchers" src="https://img.shields.io/github/watchers/erivlis/graphinate.svg">
    </td>
  </tr>
  <tr>
    <td>Tools</td>
    <td>
      <img alt="Static Badge" src="https://img.shields.io/badge/PyCharm-21D789.svg?logo=PyCharm&logoColor=black&labelColor=21D789&color=FCF84A">
      <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;"></a>
    </td>
  </tr>
  <tr>
    <td>CI/CD</td>
    <td>
      <a href="https://github.com/erivlis/graphinate/actions/workflows/test.yml"><img alt="Tests" src="https://github.com/erivlis/graphinate/actions/workflows/test.yml/badge.svg?branch=master"></a>
      <a href="https://github.com/erivlis/graphinate/actions/workflows/publish.yml"><img alt="Publish" src="https://github.com/erivlis/graphinate/actions/workflows/publish.yml/badge.svg"></a>
      <a href="https://github.com/erivlis/graphinate/actions/workflows/publish-docs.yaml"><img alt="Publish Docs" src="https://github.com/erivlis/graphinate/actions/workflows/publish-docs.yaml/badge.svg"></a>
    </td>
  </tr>
  <tr>
    <td>Scans</td>
    <td>
      <a href="https://codecov.io/gh/erivlis/graphinate"><img alt="Coverage" src="https://codecov.io/gh/erivlis/graphinate/graph/badge.svg?token=POODT8M9NV"/></a>
      <br>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_graphinate"><img alt="Quality Gate Status" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_graphinate&metric=alert_status"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_graphinate"><img alt="Security Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_graphinate&metric=security_rating"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_graphinate"><img alt="Maintainability Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_graphinate&metric=sqale_rating"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_graphinate"><img alt="Reliability Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_graphinate&metric=reliability_rating"></a>
      <br>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_graphinate"><img alt="Lines of Code" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_graphinate&metric=ncloc"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_graphinate"><img alt="Vulnerabilities" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_graphinate&metric=vulnerabilities"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_graphinate"><img alt="Bugs" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_graphinate&metric=bugs"></a>
      <br>
      <a href="https://app.codacy.com/gh/erivlis/graphinate/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade"><img alt="Codacy Badge" src="https://app.codacy.com/project/badge/Grade/54b33c3f7313448f9471d01e2a06f037"></a>
      <a href="https://scrutinizer-ci.com/g/erivlis/graphinate"><img alt="Scrutinizer" src="https://scrutinizer-ci.com/g/erivlis/graphinate/badges/quality-score.png?b=main"></a>
      <!--a href="https://snyk.io/test/github/erivlis/graphinate"><img alt="Snyk" src="https://snyk.io/test/github/erivlis/Graphinate/badge.svg"></a -->
    </td>
  </tr>
</table>

---------------------

## Introduction

### What is Graphinate?

**Graphinate** is a python library that aims to simplify the generation of Graph Data Structures from Data Sources.

It can help create an efficient retrieval pipeline from a given data source, while also enabling the developer to easily
map data payloads and hierarchies to a Graph.

In addition, there are several modes of output to enable examination of the Graph, and it's content.

**Graphinate** utilizes and builds upon the excellent [**_NetworkX_**](https://networkx.org/).

### Links

- Website (including documentation): https://erivlis.github.io/graphinate
- Source: https://github.com/erivlis/graphinate
- Package: https://pypi.org/project/graphinate

## Quick Start

### Install

**Graphinate** is available on PyPI:

```shell
pip install graphinate
```

To install with server support

```shell
pip install graphinate[server]
```

**Graphinate** officially supports Python >= 3.9.

### Example

```python
import graphinate

N: int = 8

# Define GraphModel
graph_model = graphinate.model(name="Octagonal Graph")


# Register edges supplier function
@graph_model.edge()
def edge():
    for i in range(N):
        yield {'source': i, 'target': i + 1}
    yield {'source': N, 'target': 0}


# Materialize the GraphModel
graphinate.materialize(graph_model)
```

> [!NOTE]
> ### `graphinate.model` function
> This function creates `GraphModel` class that is used to declaratively register _Edge_ and/or _Node_ data
> supplier functions by using the `GraphModel.node()` and `GraphModel.edge()` decorators.
> ### `graphinate.materialize` function
> This function can be used to easily generate an output from a `GraphModel` instance.
> By default, it will prompt the user to choose the output format, using a popup GUI dialog box.

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
Usage: python -m graphinate save [OPTIONS]

Options:
  -m, --model MODEL  A GraphModel instance reference {module-
                     name}:{GraphModel-instance-variable-name} For example,
                     given var `model=GraphModel()` defined in app.py file,
                     then the  reference should be app:model
  --help             Show this message and exit.
```

#### Server

```
Usage: python -m graphinate server [OPTIONS]

Options:
  -m, --model MODEL   A GraphModel instance reference {module-
                      name}:{GraphModel-instance-variable-name} For example,
                      given var `model=GraphModel()` defined in app.py file,
                      then the  reference should be app:model
  -p, --port INTEGER  Port number.
  --help              Show this message and exit.
```

## Gallery

### Python AST

![d3_graph_ast](https://github.com/erivlis/graphinate/assets/9897520/9e7e1ed2-3a5c-41fe-8c5f-999da4b741ff)

### GitHub Repository

![repo_graph](https://github.com/erivlis/graphinate/assets/9897520/9c044bbe-1f21-41b8-b879-95b8362ad48d)

### Python AST - 3D Force-Directed Animation

<video width="400"  controls>
  <source src="https://github.com/erivlis/graphinate/assets/9897520/2e9a53b1-5686-4683-a0e4-fbffa850a27b" type="video/mp4">
</video>

### Web Page Links

![Web Page Links](https://github.com/erivlis/graphinate/assets/9897520/ea5b00a2-75d1-4d0e-86af-272f20973149)

## Development

### Ruff

```shell
ruff check src
```

### Test

#### Standard (cobertura) XML Coverage Report

```shell
 python -m pytest tests -n auto --cov=src --cov-branch --doctest-modules --cov-report=xml --junitxml=test_results.xml
```

#### HTML Coverage Report

```shell
python -m pytest tests -n auto --cov=src --cov-branch --doctest-modules --cov-report=html --junitxml=test_results.xml
```

### Docs

#### test

```shell
python -m mkdocs serve
```

#### build

```shell
python -m mkdocs build
```

## Acknowledgements

### Dependencies

#### Python

<a href="https://palletsprojects.com/p/click/"><img height="60" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://click.palletsprojects.com/en/7.x/_images/click-logo.png" alt="Click Logo."></a>
<a href="https://github.com/Delgan/loguru"><img height="60" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://raw.githubusercontent.com/Delgan/loguru/master/docs/_static/img/logo.png" alt="Loguru Logo."></a>
<a href="https://matplotlib.org/"><img height="60" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://matplotlib.org/_static/logo_dark.svg" alt="matplotlib Logo."></a>
<a href="https://networkx.org/"><img height="60" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://networkx.org/_static/networkx_logo.svg" alt="NetworkX Logo."></a>
<a href="https://strawberry.rocks/"><img height="60" style="padding: 5px; background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://github.com/strawberry-graphql/strawberry/raw/main/.github/logo.png" alt="Strawberry GraphQL Logo."></a>

#### Javascript and HTML

<a href="https://vasturiano.github.io/3d-force-graph/"><img height="60" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="http://gist.github.com/vasturiano/02affe306ce445e423f992faeea13521/raw/preview.png" alt="3D Force-Directed Graph Logo."></a>
<a href="https://github.com/graphql-kit/graphql-voyager"><img height="60" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://github.com/graphql-kit/graphql-voyager/raw/main/docs/cover.png" alt="Graphql Voyager Logo."></a>

### Dev Tools

<a href="https://hatch.pypa.io/"><img height="60" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://hatch.pypa.io/latest/assets/images/logo.svg" alt="Hatch logo."></a>
<a href="https://squidfunk.github.io/mkdocs-material/"><img height="60" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://raw.githubusercontent.com/squidfunk/mkdocs-material/master/.github/assets/logo.svg" alt="Material for MkDocs"></a>
<a href="https://pytest.org"><img height="60" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://docs.pytest.org/en/7.4.x/_static/pytest_logo_curves.svg" alt="pytest logo."></a>
<a href="https://astral.sh/ruff"><img height="60" style="background: linear-gradient(-45deg, #FFFFFF, #CCCCCC);" src="https://astralcms.wpengine.com/wp-content/uploads/2023/03/Ruff-Logo.svg" alt="Ruff logo."></a>

### IDE

<a href="https://www.jetbrains.com/pycharm/"><img height="60" style="background: linear-gradient(-45deg, #FCF84A, #3DEA62, #21D789);" src="https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.png" alt="PyCharm logo."></a>

------

<img alt="Star Chart" src="https://forthebadge.com/images/badges/works-on-my-machine.svg">

Copyright © 2023 Eran Rivlis
