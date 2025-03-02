# CLI

## Commands

``` shell
Usage: python -m graphinate [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  save
  server
```

### Save

```console
Usage: python -m graphinate save [OPTIONS]

Options:
  -m, --model MODEL  A GraphModel instance reference {module-
                     name}:{GraphModel-instance-variable-name} For example,
                     given var `model=GraphModel()` defined in app.py file,
                     then the reference should be app:model
  --help             Show this message and exit.
```

### Server

!!! tip

    requires the `server` extra to be installed.

      ```shell
      pip install graphinate[server]
      ```

```console
Usage: python -m graphinate server [OPTIONS]

Options:
  -m, --model MODEL   A GraphModel instance reference {module-
                      name}:{GraphModel-instance-variable-name} For example,
                      given var `model=GraphModel()` defined in app.py file,
                      then the  reference should be app:model
  -p, --port INTEGER  Port number.
  --help              Show this message and exit.
```