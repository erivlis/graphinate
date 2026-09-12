import importlib
import json
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

import rich_click as click
from loguru import logger
from strawberry import Schema

from . import GraphModel, builders, graphql
from .renderers.graphql import DEFAULT_PORT


def _configure_logging(debug: bool = False) -> None:
    logger.remove()
    log_level = 'DEBUG' if debug else 'INFO'
    logger.add(sys.stderr, level=log_level)


def _get_kwargs(ctx: click.Context) -> dict:
    return dict([item.strip('--').split('=') for item in ctx.args if item.startswith("--")])  # NOSONAR


def import_from_string(import_str: str) -> GraphModel:
    """Import an object from a string reference {module-name}:{variable-name}
    For example, if `model: GraphModel = GraphModel(...)` is a variable defined in an app.py file,
     then the reference would be app:model.
    """

    if not isinstance(import_str, str):
        raise ImportFromStringError(f"{import_str} is not a string")

    module_name, _, attrs_names_str = import_str.partition(':')
    if not module_name or not attrs_names_str:
        message = f"Import string '{import_str}' must be in format '<module>:<attribute>'."
        raise ImportFromStringError(message)

    try:
        module: ModuleType = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name != module_name:
            raise exc from None
        message = f"Could not import module '{module_name}'."
        raise ImportFromStringError(message) from exc

    instance_candidate: ModuleType | GraphModel = module
    try:
        for attr_name in attrs_names_str.split('.'):
            instance_candidate = getattr(instance_candidate, attr_name)
    except AttributeError as e:
        message = f"Attribute '{attrs_names_str}' not found in import string reference '{import_str}'."
        raise ImportFromStringError(message) from e

    if isinstance(instance_candidate, GraphModel):
        return instance_candidate
    else:
        raise ImportFromStringError(f"GraphModel instance cannot be determined from reference '{import_str}'")


class ImportFromStringError(Exception):
    pass


class GraphModelType(click.ParamType):
    name = "MODEL"

    def convert(self,
                value: Any,
                param: click.Parameter | None,
                ctx: click.Context) -> GraphModel:  # type: ignore[override]
        if isinstance(value, GraphModel):
            return value

        try:
            return import_from_string(value)
        except Exception as e:
            self.fail(str(e))


model_option: Callable[[...], click.Option] = click.option(
    '-m', '--model',
    type=GraphModelType,
    help="A GraphModel instance reference {module-name}:{GraphModel-instance-variable-name}"
         " For example given a var `model=GraphModel()` defined in app.py file, then the"
         " reference would be app:model"
)


@click.group()
@click.option(
    '--debug/--no-debug',
    default=False,
    envvar='GRAPHINATE_DEBUG',
    help='Enable or disable debug mode (can also be set via GRAPHINATE_DEBUG env var).'
)
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    _configure_logging(debug)


@cli.command()
@model_option
@click.option('--debug/--no-debug', envvar='GRAPHINATE_DEBUG', default=None,
              help='Enable or disable debug mode (can also be set via GRAPHINATE_DEBUG env var).')
@click.pass_context
def save(ctx: click.Context, model: GraphModel, debug: bool | None = None) -> None:
    if debug is not None:
        ctx.obj['debug'] = debug
        _configure_logging(debug)

    file_path = Path(f"{model.name}.d3_graph.json")

    if file_path.is_absolute():
        raise click.ClickException("Please provide a relative file path for saving the graph.")

    if file_path.parent != Path('.'):
        raise click.ClickException("Saving to subdirectories is not supported. Please provide a file name only.")

    if file_path.exists():
        click.confirm(f"The file '{file_path}' already exists. Do you want to overwrite it?", abort=True)

    kwargs = _get_kwargs(ctx)
    with open(file_path, mode='w') as fp:
        graph = builders.D3Builder(model, **kwargs).build()
        json.dump(graph, fp=fp, default=str, **kwargs)


@cli.command()
@model_option
@click.option('-p', '--port', type=int, default=DEFAULT_PORT, help='Port number.')
@click.option('-b', '--browse', type=bool, default=False, help='Open server address in browser.')
@click.option('--debug/--no-debug', envvar='GRAPHINATE_DEBUG', default=None,
              help='Enable or disable debug mode (can also be set via GRAPHINATE_DEBUG env var).')
@click.pass_context
def server(ctx: click.Context, model: GraphModel, port: int, browse: bool, debug: bool | None = None) -> None:
    if debug is None:
        debug = ctx.obj.get('debug', False)
    else:
        ctx.obj['debug'] = debug
    _configure_logging(debug)

    message = """
     ██████╗ ██████╗  █████╗ ██████╗ ██╗  ██╗██║███╗   ██╗ █████╗ ████████╗███████╗
    ██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██║  ██║██║████╗  ██║██╔══██╗╚══██╔══╝██╔════╝
    ██║  ███╗██████╔╝███████║██████╔╝███████║██║██╔██╗ ██║███████║   ██║   █████╗
    ██║   ██║██╔══██╗██╔══██║██╔═══╝ ██╔══██║██║██║╚██╗██║██╔══██║   ██║   ██╔══╝
    ╚██████╔╝██║  ██║██║  ██║██║     ██║  ██║██║██║ ╚████║██║  ██║   ██║   ███████╗
     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝   ╚══════╝"""
    click.echo(message)
    schema: Schema = builders.GraphQLBuilder(model).build()
    graphql.server(schema, port=port, browse=browse, debug=debug, **_get_kwargs(ctx))
