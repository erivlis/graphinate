import graphinate
from graphinate.graphs.networkx import NetworkxGraphType
from graphinate.plot import show
from helpers import _user

DEPTH = 1

graph_model = graphinate.GraphModel(name='github-followers')


def _followers(user_id: str | None = None, depth: int = 0, **kwargs):
    user = _user(user_id)
    for follower in user.get_followers():
        yield {'source': user.login, 'target': follower.login}
        if depth < DEPTH:
            yield from _followers(follower.login, depth=depth + 1, **kwargs)


@graph_model.edge()
def followed_by(user_id: str | None = None, **kwargs):
    yield from _followers(user_id, **kwargs)


if __name__ == '__main__':
    networkx_graph = graphinate.graphs.NetworkxGraph(graph_model, graph_type=NetworkxGraphType.Graph)

    params = {
        # 'user_id': 'erivlis'
        'user_id': 'jhwang1992 '
        # 'user_id': 'andybrewer'
        # 'user_id' "strawberry-graphql"
    }
    graph = networkx_graph.build(**params)
    show(graph)
