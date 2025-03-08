import fnmatch
import operator
import pathlib

from magika import Magika

import graphinate


def load_ignore_patterns(ignore_files):
    patterns = set()
    for ignore_file in ignore_files:
        if pathlib.Path(ignore_file).exists():
            with open(ignore_file) as file:
                patterns.update(line.strip() for line in file if line.strip() and not line.startswith('#'))

    expand_patterns = {f"**/*{p}" if p.startswith('/') else f"**/*/{p}" for p in patterns}
    patterns.update(expand_patterns)
    return patterns


def is_ignored(path, patterns):
    return any(fnmatch.fnmatch(path.as_posix(), pattern) for pattern in patterns)


def create_filesystem_graph_model(input_folder='.', ignore_files=['.ignore', '.gitignore', '.dockerignore']):
    """
    Create a graph model of the file system structure.

    Args:
        input_folder (str): The folder to start the traversal from. Defaults to the current folder.
        ignore_files (list): A list of files containing ignore patterns.
                             Defaults to ['.ignore', '.gitignore', '.dockerignore'].

    Returns:
        GraphModel: A graph model representing the file system structure.
    """
    graph_model = graphinate.model(name="File System Graph")
    magika = Magika()

    root_folder = pathlib.Path(input_folder)
    ignore_patterns = load_ignore_patterns(ignore_files)

    def file_type(path: pathlib.Path) -> str:
        if path.is_file():
            return magika.identify_path(path).output.ct_label
        elif path.is_dir():
            return 'folder'
        else:
            return 'other'

    as_posix = operator.methodcaller('as_posix')

    @graph_model.node(file_type, key=as_posix, value=as_posix)
    def file_node():
        yield root_folder
        for path in root_folder.rglob('*'):
            if not is_ignored(path, ignore_patterns, ):
                yield path

    @graph_model.edge()
    def contains():
        for path in root_folder.rglob('*'):
            if not is_ignored(path, ignore_patterns):
                yield {
                    'source': path.parent.as_posix(),
                    'target': path.as_posix()
                }

    return graph_model


if __name__ == '__main__':
    input_folder = '..'  # Default to the current folder
    ignore_files = ['.ignore', '.gitignore']  # Example list of ignore files
    filesystem_model = create_filesystem_graph_model(input_folder, ignore_files)

    schema = graphinate.builders.GraphQLBuilder(filesystem_model).build()
    graphinate.graphql.server(schema)
