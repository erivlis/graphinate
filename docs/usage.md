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

## Libarary

### Modeling

#### :material-code-tags: `graphinate.GraphModel`

Graphinate defines the _**GraphModel**_ Class which can be used to declaratively register Edge and/or Node data
supplier functions using the _GraphModel.node()_ and _GraphMode.edge()_ decorators.


### Functions

#### :material-function: `graphinate.materialize`

This function can be used to easily generate an output from a `GraphModel` instance.
By default, it will prompt the user to choose the output format, using a popup dialog.

### Builders

> TBD

### Materializers

> TBD