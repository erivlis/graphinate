"""
https://www.pnas.org/doi/10.1073/pnas.0709247105
"""

from datetime import timedelta
from typing import Optional

from _client import github_commits, github_repositories, github_user
from github.GitCommit import GitCommit


def commit_interval(user_id: Optional[str] = None,
                    repository_id: Optional[str] = None,
                    commit_id: Optional[str] = None):
    github_user(user_id)
    for repo in github_repositories(user_id, repository_id):
        for commit in github_commits(repo, commit_id):
            git_commit: GitCommit = commit.commit
            parents = git_commit.parents
            parent_git_commit: GitCommit = parents[0] if parents else None
            author_datetime = git_commit.author.date
            parent_author_datetime = parent_git_commit.author.date if parent_git_commit else author_datetime
            interval: timedelta = author_datetime - parent_author_datetime
            s = interval.total_seconds()
            yield s


series = list(commit_interval('erivlis', 'graphinate'))
series.reverse()

print(series)
