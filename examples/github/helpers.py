import functools
import os

from github import Auth, Github
from github.Commit import Commit
from github.File import File

token = os.getenv('GITHUB_TOKEN')

# using an access token
auth = Auth.Token(token)

# Public Web Github
g = Github(auth=auth)


# or Github Enterprise with custom hostname
# g = Github(auth=auth, base_url='https://{hostname}/api/v3')


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
