"""
pip install PyGithub
"""
import itertools
import operator
import pathlib
from typing import Optional

import graphinate
from helpers import _user, _repositories, _commits, _files


def repo_graph_model():
    graph_model = graphinate.GraphModel(name='github-repository')

    @graph_model.edge
    def github(user_id: Optional[str] = None,
               repository_id: Optional[str] = None,
               commit_id: Optional[str] = None,
               file_id: Optional[str] = None,
               **kwargs):
        user = _user(user_id)
        for repo in _repositories(user_id, repository_id):
            yield {'source': (user.login,), 'target': (user.login, repo.name)}
            for commit in _commits(repo, commit_id):
                yield {'source': (user.login, repo.name), 'target': (user.login, repo.name, commit.sha)}
                for file in _files(commit, file_id):
                    yield {'source': (user.login, repo.name, commit.sha),
                           'target': (user.login, repo.name, commit.sha, file.filename)}

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
                                 key=operator.attrgetter('filename'),
                                 value=operator.attrgetter('raw_data'),
                                 label=operator.itemgetter('filename'))

    @user_node
    def user(user_id: Optional[str] = None, **kwargs):
        yield _user(user_id)

    @repository_node
    def repository(user_id: Optional[str] = None,
                   repository_id: Optional[str] = None,
                   **kwargs):
        repos = _repositories(user_id, repository_id)
        for repo in repos:
            yield repo

    @commit_node
    def commit(user_id: Optional[str] = None,
               repository_id: Optional[str] = None,
               commit_id: Optional[str] = None,
               **kwargs):
        for repo in _repositories(user_id, repository_id):
            yield from _commits(repo, commit_id)

    def file_type(user_id: Optional[str] = None,
                  repository_id: Optional[str] = None,
                  commit_id: Optional[str] = None,
                  file_type_id: Optional[str] = None,
                  **kwargs):
        def group_key(file):
            return pathlib.PurePath(file).suffix

        for repo in _repositories(user_id, repository_id):
            for commit in _commits(repo, commit_id):
                yield from ((k, list(g)) for k, g in
                            itertools.groupby(sorted(_files(commit), key=group_key), group_key))

    @file_node
    def file(user_id: Optional[str] = None,
             repository_id: Optional[str] = None,
             commit_id: Optional[str] = None,
             file_id: Optional[str] = None,
             **kwargs):
        for repo in _repositories(user_id, repository_id):
            for commit in _commits(repo, commit_id):
                yield from _files(commit, file_id)

    return graph_model


if __name__ == '__main__':
    repo_model = repo_graph_model()

    params = {
        # 'user_id': 'erivlis',
        # 'repository_id': 'graphinate',
        # 'user_id': 'andybrewer',
        # 'repository_id': 'operation-go',
        # 'commit_id': None,
        # 'file_id': 'README.md',
        # 'user_id' "strawberry-graphql"
    }

    graphinate.display("GitHub Repository Graph", repo_model, **params)