import functools
import json

import click

from . import builders
from .materializers import materialize
from .modeling import GraphModel
from .server import DEFAULT_PORT, run_graphql
from .tools.importer import import_from_string


def _get_kwargs(ctx) -> dict:
    return dict([item.strip('--').split('=') for item in ctx.args if item.startswith("--")])


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
    with open(f"{model.name}.json", mode='w') as fp:
        materialize(model=model,
                    builder=builders.D3Builder,
                    actualizer=functools.partial(json.dump, fp=fp, default=str),
                    **_get_kwargs(ctx))


@cli.command()
@model_option
@click.option('-p', '--port', type=int, default=DEFAULT_PORT, help='Port number.')
@click.pass_context
def server(ctx, model, port):
    materialize(model=model,
                builder=builders.GraphQLBuilder,
                actualizer=functools.partial(run_graphql, port=port),
                **_get_kwargs(ctx))
