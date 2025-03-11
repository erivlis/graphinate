import operator
from pathlib import Path
from tempfile import TemporaryDirectory

import git

import graphinate


def create_graph_model(repo: git.Repo):
    # Fetch all branches from the remote
    repo.git.fetch('--all')

    graph_model = graphinate.GraphModel(name='Git Repository Graph')

    @graph_model.node(operator.itemgetter('type'), key=operator.itemgetter('id'), label=operator.itemgetter('label'))
    def commit():
        for b in repo.remote().refs:
            for c in repo.iter_commits(b):
                branch = b.name.replace('origin/', '')
                for char in '-/. ':
                    if char in branch:
                        branch = branch.replace(char, '_')

                yield {'id': c.hexsha,
                       'type': branch,
                       'branch': b.name,
                       'label': c.summary}
                for f in c.stats.files:
                    yield {'id': f,
                           'type': 'file',
                           'branch': b.name,
                           'label': f}

    @graph_model.edge()
    def branch():
        for b in repo.remote().refs:
            for c in repo.iter_commits(b):
                if c.parents:
                    yield {'source': c.parents[0].hexsha, 'target': c.hexsha}
                    for f in c.stats.files:
                        yield {'source': c.hexsha, 'target': f}

    return graph_model


def git_commits(repo_url: str):
    with TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir)

        with git.Repo.clone_from(repo_url, repo_path) as repo:
            model = create_graph_model(repo)
            schema = graphinate.builders.GraphQLBuilder(model).build()
            graphinate.graphql.server(schema)


if __name__ == '__main__':
    # git_commits(repo_url='https://github.com/google/magika.git')
    git_commits(repo_url='https://github.com/erivlis/mappingtools.git')
