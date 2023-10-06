import graphinate
from pipdeptree._cli import get_options
from pipdeptree._discovery import get_installed_distributions
from pipdeptree._models import PackageDAG
from pipdeptree._non_host import handle_non_host_target


def dependency_graph_model():
    options = get_options(args=None)
    handle_non_host_target(options)

    pkgs = get_installed_distributions(local_only=options.local_only, user_only=options.user_only)
    tree = PackageDAG.from_pkgs(pkgs)

    graph_model = graphinate.model(name="Dependency Graph")

    @graph_model.edge()
    def dependency():
        for p, d in tree.items():
            for c in d:
                yield {'source': p.project_name, 'target': c.project_name}

    return graph_model


if __name__ == '__main__':
    dependency_model = dependency_graph_model()
    graphinate.materialize(
        dependency_model,
        builder=graphinate.builders.GraphQLBuilder,
        actualizer=graphinate.plot
    )
