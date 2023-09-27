# Usage

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

## Library

### Top level Functions

#### :material-function: `graphinate.model`

Top level function that creates a _**GraphModel**_

#### :material-function: `graphinate.materialize`

This function can be used to easily generate an output from a `GraphModel` instance.
By default, it will prompt the user to choose the output format, using a popup dialog.

### Modeling

#### :material-code-tags: `graphinate.GraphModel`

Graphinate defines the `GraphModel` Class which can be used to declaratively register Edge and/or Node data
supplier functions using the `GraphModel.node()` and `GraphMode.edge()` decorators.

#### :material-code-tags: `graphinate.NodeModel`

> TBD

### Builders

#### :material-code-tags: `graphinate.builders.NetworkxBuilder`

Used to generate a NetworkX Graph instance.

#### :material-code-tags: `graphinate.builders.D3Builder`

Used to generate a D3 Graph instance (i.e. a Dict).

#### :material-code-tags: `graphinate.builders.GraphQLBuilder`

Used to generate a Strawberry GraphQL Schema instance

### Actualizers

> TBD

### Materializers

> TBD