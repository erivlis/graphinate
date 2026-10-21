---
title: "GEP-016: CLI Argument Parsing & Path Safety"
description: "The current CLI implementation uses manual string parsing to handle dynamic arguments and enforces strict file path"
icon: lucide/git-branch
status: active
---

# GEP-016: CLI Argument Parsing & Path Safety

| Field       | Value                              |
|:------------|:-----------------------------------|
| **GEP**     | 16                                 |
| **Title**   | CLI Argument Parsing & Path Safety |
| **Author**  | Eran Rivlis                        |
| **Delegate**| The Council                   |
| **Status**  | Active                             |
| **Type**    | Standards Track                    |
| **Created** | 2025-12-25                         |
| **Updated** | 2026-10-22                    |

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

## Rationale

Evaluating against the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):
- **Safety (The Golem):** Replacing ad-hoc string splitting with validated argument parsing eliminates unexpected CLI crashes and injection vulnerabilities.
- **Clarity (Feynman):** Standard option formatting conforms to established CLI UX expectations.
- **Harmony (The Steward):** Preserves backward compatibility where feasible, migrating to Typer CLI.

## Specification

### Argument Parsing

Replace `ctx.args` parsing with structured options or Typer dynamic parameter types.

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

## Reference Implementation

- Implementation: [`src/graphinate/cli.py`](file:///C:/dev/erivlis/graphinate/src/graphinate/cli.py)
- Tests: [`tests/graphinate/test_cli.py`](file:///C:/dev/erivlis/graphinate/tests/graphinate/test_cli.py)

## Change Log

* **2025-12-25:** Initial draft.
* **2026-10-17:** Implemented robust CLI argument parsing and relaxed path safety in Typer CLI.
* **2026-10-22:** Rebased into GEP standard with frontmatter and Council alignment.
