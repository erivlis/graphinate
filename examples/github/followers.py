"""
Defines a function `followers_graph_model` that creates a graph model representing GitHub followers.
It recursively fetches followers of a given user up to a specified maximum depth.
The function yields edges between users in the graph.
"""

from typing import Optional

from _client import github_user  # see _client.py

import graphinate

DEPTH = 0


def followers_graph_model(max_depth: int = DEPTH):
    """
    Create a graph model representing GitHub followers.

    Args:
        max_depth (int): The maximum depth to fetch followers recursively (default is 0).

    Returns:
        GraphModel: A graph model representing GitHub followers.
    """

    graph_model = graphinate.model(name='Github Followers Graph')

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
        'user_id': 'erivlis'
        # 'user_id': 'andybrewer'
        # 'user_id' "strawberry-graphql"
    }

    builder = graphinate.builders.GraphQLBuilder(followers_model, graph_type=graphinate.GraphType.DiGraph)
    schema = builder.build(default_node_attributes={'type': 'user'}, **params)
    graphinate.graphql.server(schema)
