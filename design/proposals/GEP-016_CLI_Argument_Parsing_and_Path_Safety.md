# GEP-016: CLI Argument Parsing & Path Safety

| Field       | Value                              |
|:------------|:-----------------------------------|
| **GEP**     | 16                                 |
| **Title**   | CLI Argument Parsing & Path Safety |
| **Author**  | Eran Rivlis                        |
| **Status**  | Draft                              |
| **Type**    | Standards Track                    |
| **Created** | 2025-12-25                         |

## Abstract

The current CLI implementation uses manual string parsing to handle dynamic arguments and enforces strict file path
restrictions. This proposal advocates for using standard `click` features for argument parsing and relaxing the file
system restrictions to improve usability and safety.

## Motivation

**Issues:**

1. **Unsafe Parsing:** The `_get_kwargs` function manually splits strings like `--key=value`. This bypasses `click`'s
   validation and type conversion, leading to potential errors and security risks.
2. **Restrictive Paths:** The `save` command prevents saving files to subdirectories. This limits automation and
   organization.

## Specification

### Argument Parsing

Replace `ctx.args` parsing with `click.option` using `multiple=True` or a custom `DictParamType`.

```python
@click.option('--config', '-c', multiple=True, help="Key-value pairs like key=value")
def command(config):
    kwargs = dict(item.split('=') for item in config)
```

### Path Safety

Remove the check `file_path.parent != Path('.')`. Instead:

1. Allow any valid path.
2. Create parent directories if they don't exist (optional, or fail with a clear message).
3. Prompt for confirmation if overwriting (already implemented).

## Backwards Compatibility

* **Arguments:** Changing from arbitrary flags (e.g., `--foo=bar`) to a structured flag (e.g., `-c foo=bar`) is a
  breaking change for the CLI syntax.
* **Paths:** Relaxing restrictions is backward compatible.
