"""
pip install PyGithub
"""
import operator
import os
from typing import Generator, Any, Mapping

from github import Auth
from github import Github
from github.Commit import Commit
from github.File import File
from github.Repository import Repository

import graphinate
from graphinate.plot import show

token = os.getenv('GITHUB_TOKEN')

# using an access token
auth = Auth.Token(token)

# Public Web Github
g = Github(auth=auth)


# or Github Enterprise with custom hostname
# g = Github(auth=auth, base_url="https://{hostname}/api/v3")


def clean(data: Mapping):
    return {k: v for k, v in data.items()}


def _repositories(repo_id: str | None = None) -> Generator[Repository, Any, None]:
    if repo_id and (repo := g.get_user().get_repo(name=repo_id)):
        yield repo
    else:
        yield from g.get_user().get_repos()


def _commits(repo, commit_id: str | None = None):
    if commit_id and (commit := repo.get_commit(sha=commit_id)):
        yield commit
    else:
        yield from repo.get_commits()


def _files(commit: Commit, file_id: str | None = None):
    files: list[File] = commit.files
    if file_id:
        yield from (file for file in files if file.filename == file_id)
    else:
        yield from files


graph_model = graphinate.GraphModel(name="Github")

repository_node = graph_model.node(type="repository",
                                   key=operator.attrgetter("name"),
                                   value=operator.attrgetter("raw_data"),
                                   label=operator.itemgetter("name"))

commit_node = graph_model.node(type="commit",
                               parent_type="repository",
                               key=operator.attrgetter("sha"),
                               value=operator.attrgetter("raw_data"),
                               label=operator.itemgetter("sha"))

file_node = graph_model.node(type="file",
                             parent_type="commit",
                             key=operator.attrgetter("filename"),
                             value=operator.attrgetter("raw_data"),
                             label=operator.itemgetter("filename"))


@repository_node
def repositories(repo_id: str | None = None, **kwargs):
    repos = _repositories(repo_id)
    for repo in repos:
        yield repo


@commit_node
def commits(repo_id: str | None = None, commit_id: str | None = None, **kwargs):
    for repo in _repositories(repo_id):
        yield from _commits(repo, commit_id)


@file_node
def files(repo_id: str | None = None, commit_id: str | None = None, file_id: str | None = None, **kwargs):
    for repo in _repositories(repo_id):
        for commit in _commits(repo, commit_id):
            yield from _files(commit, file_id)


if __name__ == '__main__':
    networkx_graph = graphinate.graphs.NetworkxGraph(graph_model)
    graph = networkx_graph.build()
    show(graph)
