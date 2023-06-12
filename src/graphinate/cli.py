import click


@click.group()
def cli(ctx, *args, **kwargs):
    pass


@cli.command()
def create(ctx, *args, **kwargs):
    pass


@cli.command()
def server(ctx, *args, **kwargs):
    pass
