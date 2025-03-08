import itertools
import operator
import pathlib
from typing import Optional

from _client import github_commits, github_files, github_repositories, github_user  # see _client.py

import graphinate


def repo_graph_model():  # noqa: C901
    """
    Create a graph model for GitHub repositories.

    Returns:
        GraphModel: A graph model representing GitHub repositories with nodes and edges.
    """

    graph_model = graphinate.model(name='GitHub Repository Graph')

    @graph_model.edge()
    def github(user_id: Optional[str] = None,
               repository_id: Optional[str] = None,
               commit_id: Optional[str] = None,
               file_id: Optional[str] = None,
               **kwargs):
        user = github_user(user_id)
        for repo in github_repositories(user_id, repository_id):
            yield {'source': (user.login,), 'target': (user.login, repo.name)}
            for commit in github_commits(repo, commit_id):
                yield {
                    'source': (user.login, repo.name),
                    'target': (user.login, repo.name, commit.sha)
                }
                for file in github_files(commit, file_id):
                    yield {
                        'source': (user.login, repo.name, commit.sha),
                        'target': (user.login, repo.name, commit.sha, file.filename)
                    }

    user_node = graph_model.node(key=operator.attrgetter('login'),
                                 value=operator.attrgetter('raw_data'),
                                 label=operator.itemgetter('name'))

    repository_node = graph_model.node(parent_type='user',
                                       key=operator.attrgetter('name'),
                                       value=operator.attrgetter('raw_data'),
                                       label=operator.itemgetter('name'))

    def commit_label(commit):
        return commit['sha'][-7:]

    commit_node = graph_model.node(parent_type='repository',
                                   key=operator.attrgetter('sha'),
                                   value=operator.attrgetter('raw_data'),
                                   label=commit_label)

    file_node = graph_model.node(parent_type='commit',
                                 unique=True,
                                 key=operator.attrgetter('filename'),
                                 value=operator.attrgetter('raw_data'),
                                 label=operator.itemgetter('filename'))

    @user_node
    def user(user_id: Optional[str] = None, **kwargs):
        yield github_user(user_id)

    @repository_node
    def repository(user_id: Optional[str] = None,
                   repository_id: Optional[str] = None,
                   **kwargs):
        repos = github_repositories(user_id, repository_id)
        yield from repos

    @commit_node
    def commit(user_id: Optional[str] = None,
               repository_id: Optional[str] = None,
               commit_id: Optional[str] = None,
               **kwargs):
        for repo in github_repositories(user_id, repository_id):
            yield from github_commits(repo, commit_id)

    def file_type(user_id: Optional[str] = None,
                  repository_id: Optional[str] = None,
                  commit_id: Optional[str] = None,
                  file_type_id: Optional[str] = None,
                  **kwargs):
        def group_key(file):
            return pathlib.PurePath(file).suffix

        for repo in github_repositories(user_id, repository_id):
            for commit in github_commits(repo, commit_id):
                yield from ((k, list(g)) for k, g in
                            itertools.groupby(
                                sorted(github_files(commit),
                                       key=group_key), group_key
                            ))

    @file_node
    def file(user_id: Optional[str] = None,
             repository_id: Optional[str] = None,
             commit_id: Optional[str] = None,
             file_id: Optional[str] = None,
             **kwargs):
        for repo in github_repositories(user_id, repository_id):
            for commit in github_commits(repo, commit_id):
                yield from github_files(commit, file_id)

    return graph_model


if __name__ == '__main__':
    repo_model = repo_graph_model()

    params = {
        'user_id': 'erivlis',
        'repository_id': 'graphinate',
        # 'user_id': 'andybrewer',
        # 'repository_id': 'operation-go',
        # 'commit_id': None,
        # 'file_id': 'README.md',
        # 'user_id' "strawberry-graphql"
    }

    schema = graphinate.builders.GraphQLBuilder(repo_model).build(**params)
    graphinate.graphql.server(schema)
