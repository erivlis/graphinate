import functools
import json

import click

from . import builders
from .materializers import materialize
from .modeling import GraphModel
from .server import DEFAULT_PORT, run_graphql
from .tools.importer import import_from_string


@click.group()
def cli(*args, **kwargs):
    pass


@cli.command()
@click.argument('model')
def save(model, *args, **kwargs):
    graph_model: GraphModel = import_from_string(model) if isinstance(model, str) else model
    with open(f"{graph_model.name}.json", mode='w') as fp:
        materialize(model=graph_model,
                    builder=builders.D3Builder,
                    actualizer=functools.partial(json.dump, fp=fp, default=str))


@cli.command()
@click.argument('model')
@click.option('-p', '--port', type=int, default=DEFAULT_PORT)
def server(model, port, *args, **kwargs):
    graph_model: GraphModel = import_from_string(model) if isinstance(model, str) else model
    materialize(model=graph_model,
                builder=builders.GraphQLBuilder,
                actualizer=functools.partial(run_graphql, port=port))
