import functools
import os
from collections.abc import Iterable
from typing import Optional, Union

from github import Auth, Github
from github.AuthenticatedUser import AuthenticatedUser
from github.Commit import Commit
from github.File import File
from github.NamedUser import NamedUser
from github.Repository import Repository

token = os.getenv('GITHUB_TOKEN')

# using an access token
auth = Auth.Token(token)

# Public Web Github
g = Github(auth=auth)


# or Github Enterprise with custom hostname
# g = Github(auth=auth, base_url='https://{hostname}/api/v3')


@functools.lru_cache
def github_user(user_id: Optional[str] = None) -> Union[NamedUser, AuthenticatedUser]:
    user = g.get_user(user_id) if user_id else g.get_user()
    return user


@functools.lru_cache
def github_repositories(user_id: Optional[str] = None, repo_id: Optional[str] = None) -> Iterable[Repository]:
    user = github_user(user_id)
    if repo_id and (repo := user.get_repo(name=repo_id)):
        return [repo]
    else:
        return user.get_repos()


def github_commits(repo: Repository, commit_id: Optional[str] = None) -> Iterable[Commit]:
    if commit_id and (commit := repo.get_commit(sha=commit_id)):
        yield commit
    else:
        yield from repo.get_commits()


def github_files(commit: Commit, file_id: Optional[str] = None) -> Iterable[File]:
    files: list[File] = commit.files
    if file_id:
        yield from [file for file in files if file.filename == file_id]
    else:
        yield from files
