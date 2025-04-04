import functools
import os
from collections.abc import Iterable
from typing import Optional, Union

# see requirements.txt
from github import Auth, Github
from github.AuthenticatedUser import AuthenticatedUser
from github.Commit import Commit
from github.File import File
from github.NamedUser import NamedUser
from github.Repository import Repository

# define a 'GITHUB_TOKEN' Env Var.
token = os.getenv('GITHUB_TOKEN')

# using an access token
auth = Auth.Token(token)

# Public Web GitHub
client = Github(auth=auth)


# or GitHub Enterprise with custom hostname
# g = Github(auth=auth, base_url='https://{hostname}/api/v3')


@functools.lru_cache
def github_user(user_id: Optional[str] = None) -> Union[NamedUser, AuthenticatedUser]:
    """
    Get the GitHub user object for the specified user ID or the authenticated user.

    Args:
        user_id (Optional[str]): The ID of the user to retrieve.
                                 If not provided, retrieve the authenticated user.

    Returns:
        Union[NamedUser, AuthenticatedUser]: The GitHub user object corresponding to the user ID provided,
                                             or the authenticated user if no user ID is specified.
    Note:
        This function requires authentication with a valid GitHub token.
    """
    user = client.get_user(user_id) if user_id else client.get_user()
    return user


@functools.lru_cache
def github_repositories(
        user_id: Optional[str] = None,
        repo_id: Optional[str] = None) -> Iterable[Repository]:
    """
    Get the GitHub repositories for the specified user ID or the authenticated user.

    Args:
        user_id (Optional[str]): The ID of the user whose repositories to retrieve.
                                 If not provided, retrieve repositories of the authenticated user.
        repo_id (Optional[str]): The ID of the repository to retrieve.
                                 If provided, only that repository will be returned.

    Returns:
        Iterable[Repository]:
        A list of GitHub repository objects corresponding to the user ID and/or repository ID provided.

    Note:
        This function requires authentication with a valid GitHub token.
    """

    user = github_user(user_id)
    if repo_id and (repo := user.get_repo(name=repo_id)):
        return [repo]
    else:
        return user.get_repos()


def github_commits(
        repo: Repository,
        commit_id: Optional[str] = None) -> Iterable[Commit]:
    """
    Retrieve commits from a GitHub repository.

    Args:
        repo (Repository): The GitHub repository object from which to retrieve commits.
        commit_id (str, optional): The ID of the commit to retrieve.
                                   If provided, only that commit will be returned.
                                   Defaults to None.

    Returns:
        Iterable[Commit]: An Iterable of Commit objects representing the commits in the repository.

    Example:
        To retrieve all commits from a repository:
        ```
        for commit in github_commits(repo):
            print(commit)
        ```

        To retrieve a specific commit by ID:
        ```
        for commit in github_commits(repo, commit_id='abcdef123456'):
            print(commit)
        ```

    Note:
        This function requires authentication with a valid GitHub token.
    """
    if commit_id and (commit := repo.get_commit(sha=commit_id)):
        yield commit
    else:
        yield from repo.get_commits()


def github_files(
        commit: Commit,
        file_id: Optional[str] = None) -> Iterable[File]:
    """
    Retrieves Files from a GitHub Commit

    Args:
        commit (Commit): A Commit object from the GitHub API.
        file_id (Optional[str]): An optional parameter specifying the filename to filter the files. Default is None.

    Returns:
        Iterable[File]: An Iterable of File objects based on the filtering criteria.

    Note:
        This function requires authentication with a valid GitHub token.
    """
    files: list[File] = commit.files
    if file_id:
        yield from [file for file in files if file.filename == file_id]
    else:
        yield from files
