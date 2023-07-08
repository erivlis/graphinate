"""
pip install PyGithub
"""
import functools
import itertools
import operator
import os
import pathlib
from typing import Mapping

from github import Auth
from github import Github
from github.Commit import Commit
from github.File import File

import graphinate
from graphinate.plot import show

token = os.getenv('GITHUB_TOKEN')

# using an access token
auth = Auth.Token(token)

# Public Web Github
g = Github(auth=auth)


# or Github Enterprise with custom hostname
# g = Github(auth=auth, base_url='https://{hostname}/api/v3')


def clean(data: Mapping):
    return {k: v for k, v in data.items()}


@functools.lru_cache
def _user(user_id=None):
    user = g.get_user(user_id) if user_id else g.get_user()
    return user


@functools.lru_cache
def _repositories(user_id: str = None, repo_id: str | None = None):
    user = _user(user_id)
    if repo_id and (repo := user.get_repo(name=repo_id)):
        return [repo]
    else:
        return user.get_repos()


def _commits(repo, commit_id: str | None = None):
    if commit_id and (commit := repo.get_commit(sha=commit_id)):
        yield commit
    else:
        yield from repo.get_commits()


def _files(commit: Commit, file_id: str | None = None):
    files: list[File] = commit.files
    if file_id:
        yield from [file for file in files if file.filename == file_id]
    else:
        yield from files


graph_model = graphinate.GraphModel(name='Github')


@graph_model.edge()
def github(user_id: str | None = None,
           repository_id: str | None = None,
           commit_id: str | None = None,
           file_id: str | None = None,
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

commit_node = graph_model.node(parent_type='repository',
                               key=operator.attrgetter('sha'),
                               value=operator.attrgetter('raw_data'),
                               label=operator.itemgetter('sha'))

file_node = graph_model.node(parent_type='commit',
                             key=operator.attrgetter('filename'),
                             value=operator.attrgetter('raw_data'),
                             label=operator.itemgetter('filename'))


@user_node
def user(user_id: str | None = None, **kwargs):
    yield _user(user_id)


@repository_node
def repository(user_id: str | None = None,
               repository_id: str | None = None,
               **kwargs):
    repos = _repositories(user_id, repository_id)
    for repo in repos:
        yield repo


@commit_node
def commit(user_id: str | None = None,
           repository_id: str | None = None,
           commit_id: str | None = None,
           **kwargs):
    for repo in _repositories(user_id, repository_id):
        yield from _commits(repo, commit_id)


def file_type(user_id: str | None = None,
              repository_id: str | None = None,
              commit_id: str | None = None,
              file_type_id: str | None = None,
              **kwargs):
    def group_key(file):
        return pathlib.PurePath(file).suffix

    for repo in _repositories(user_id, repository_id):
        for commit in _commits(repo, commit_id):
            yield from ((k, list(g)) for k, g in itertools.groupby(sorted(_files(commit), key=group_key), group_key))


@file_node
def file(user_id: str | None = None,
         repository_id: str | None = None,
         commit_id: str | None = None,
         file_id: str | None = None,
         **kwargs):
    for repo in _repositories(user_id, repository_id):
        for commit in _commits(repo, commit_id):
            yield from _files(commit, file_id)


if __name__ == '__main__':
    networkx_graph = graphinate.graphs.NetworkxGraph(graph_model)

    params = {
        # 'user_id': 'erivlis',
        # 'repository_id': 'graphinate',
        # 'user_id': 'andybrewer',
        # 'repository_id': 'operation-go',
        # 'commit_id': None,
        # 'file_id': 'README.md',
        # 'user_id' "strawberry-graphql"
    }
    graph = networkx_graph.build(**params)
    show(graph)
