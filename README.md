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

## Gallery

![d3_graph_ast](https://github.com/erivlis/graphinate/assets/9897520/9e7e1ed2-3a5c-41fe-8c5f-999da4b741ff)
![repo_graph](https://github.com/erivlis/graphinate/assets/9897520/9c044bbe-1f21-41b8-b879-95b8362ad48d)
![AST 3D Force animation](https://github.com/erivlis/graphinate/assets/9897520/2e9a53b1-5686-4683-a0e4-fbffa850a27b)

## Install

Graphinate is available on PyPI:

```console
python -m pip install graphinate 
```

Graphinate officially supports Python 3.9+.

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

## API

### By Convention

### By Configuration

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
