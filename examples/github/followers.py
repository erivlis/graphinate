from typing import Optional

import graphinate
from _client import github_user

DEPTH = 0


def followers_graph_model(max_depth: int = DEPTH):
    graph_model = graphinate.GraphModel(name='Github Followers Graph')

    def _followers(user_id: Optional[str] = None, depth: int = 0, **kwargs):
        user = github_user(user_id)
        for follower in user.get_followers():
            yield {'source': user.login, 'target': follower.login}
            if depth < max_depth:
                yield from _followers(follower.login, depth=depth + 1, **kwargs)

    @graph_model.edge()
    def followed_by(user_id: Optional[str] = None, **kwargs):
        yield from _followers(user_id, **kwargs)

    return graph_model


if __name__ == '__main__':
    followers_model = followers_graph_model(max_depth=1)

    params = {
        # 'user_id': 'erivlis'
        'user_id': 'jhwang1992 '
        # 'user_id': 'andybrewer'
        # 'user_id' "strawberry-graphql"
    }

    graphinate.materialize(
        model=followers_model,
        graph_type=graphinate.GraphType.DiGraph,
        default_node_attributes={'type': 'user'},
        **params
    )
