import git


def check_repo_health(repo_path):
    try:
        repo = git.Repo(repo_path)

        # Check if the repository is valid
        if repo.bare:
            return "Repository is bare, no issues detected."

        # Check for uncommitted changes
        if repo.is_dirty(untracked_files=True):
            return "Repository has uncommitted changes."

        # Check for merge conflicts
        if repo.index.unmerged_blobs():
            return "Repository has merge conflicts."

        # Verify repository integrity
        repo.git.fsck()
    except git.exc.InvalidGitRepositoryError:
        return "Invalid Git repository."
    except Exception as e:
        return f"An error occurred: {e}"
    else:
        return "Repository is healthy, no issues detected."

# Example usage
repo_path = r'C:\dev\erivlis\graphinate'
print(check_repo_health(repo_path))
