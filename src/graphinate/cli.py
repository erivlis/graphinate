import importlib
import json
from typing import Any

import click

from graphinate import GraphModel, builders, graphql
from graphinate.renderers.graphql import DEFAULT_PORT


def _get_kwargs(ctx) -> dict:
    return dict([item.strip('--').split('=') for item in ctx.args if item.startswith("--")])


def import_from_string(import_str: Any) -> Any:
    """Import an object from a string reference {module-name}:{variable-name}
    For example, if `model=GraphModel()` is defined in app.py file, then the
    reference would be app:model.
    """

    if not isinstance(import_str, str):
        return import_str

    module_str, _, attrs_str = import_str.partition(":")
    if not module_str or not attrs_str:
        message = f"Import string '{import_str}' must be in format '<module>:<attribute>'."
        raise ImportFromStringError(message)

    try:
        module = importlib.import_module(module_str)
    except ModuleNotFoundError as exc:
        if exc.name != module_str:
            raise exc from None
        message = f"Could not import module '{module_str}'."
        raise ImportFromStringError(message) from exc

    instance = module
    try:
        for attr_str in attrs_str.split("."):
            instance = getattr(instance, attr_str)
    except AttributeError as exc:
        message = f"Attribute '{attrs_str}' not found in module '{module_str}'."
        raise ImportFromStringError(message) from exc

    return instance


class ImportFromStringError(Exception):
    pass


class GraphModelType(click.ParamType):
    name = "MODEL"

    def convert(self, value, param, ctx) -> GraphModel:
        if isinstance(value, GraphModel):
            return value

        try:
            return import_from_string(value) if isinstance(value, str) else value
        except Exception as e:
            self.fail(str(e))


model_option = click.option('-m', '--model',
                            type=GraphModelType(),
                            help="A GraphModel instance reference {module-name}:{GraphModel-instance-variable-name}"
                                 " For example given a var `model=GraphModel()` defined in app.py file, then the"
                                 " reference would be app:model")


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@model_option
@click.pass_context
def save(ctx, model):
    kwargs = _get_kwargs(ctx)
    with open(f"{model.name}.d3_graph.json", mode='w') as fp:
        graph = builders.D3Builder(model, **kwargs).build()
        json.dump(graph, fp=fp, default=str, **kwargs)


@cli.command()
@model_option
@click.option('-p', '--port', type=int, default=DEFAULT_PORT, help='Port number.')
@click.option('-b', '--browse', type=bool, default=False, help='Open server address in browser.')
@click.pass_context
def server(ctx, model: GraphModel, port: int, browse: bool):
    message = """
     ██████╗ ██████╗  █████╗ ██████╗ ██╗  ██╗██╗███╗   ██╗ █████╗ ████████╗███████╗
    ██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██║  ██║██║████╗  ██║██╔══██╗╚══██╔══╝██╔════╝
    ██║  ███╗██████╔╝███████║██████╔╝███████║██║██╔██╗ ██║███████║   ██║   █████╗
    ██║   ██║██╔══██╗██╔══██║██╔═══╝ ██╔══██║██║██║╚██╗██║██╔══██║   ██║   ██╔══╝
    ╚██████╔╝██║  ██║██║  ██║██║     ██║  ██║██║██║ ╚████║██║  ██║   ██║   ███████╗
     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝   ╚══════╝"""
    click.echo(message)
    schema = builders.GraphQLBuilder(model).build()
    graphql(schema, port=port, browse=browse, **_get_kwargs(ctx))
