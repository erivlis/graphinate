import itertools
import operator
import sys

from pygments import lex
from pygments.lexers import guess_lexer_for_filename

import graphinate


def load_file(file_path):
    with open(file_path) as file:
        return file.read()


def tokenize_file(file_path):
    content = load_file(file_path)
    lexer = guess_lexer_for_filename(file_path, content)
    return lex(content, lexer)


def token_graph_model(file_path):
    graph_model = graphinate.model(name="Token Graph")

    def token_type(v):
        return str(v[0]).replace('.', '_')

    def token_key(v):
        return f"{v[0]}-{v[1]}"

    @graph_model.node(token_type, key=token_key)
    def token():
        yield from tokenize_file(file_path)

    @graph_model.edge(source=operator.itemgetter(0), target=operator.itemgetter(1))
    def edge():
        yield from itertools.pairwise(token_key(t) for t in tokenize_file(file_path))

    return graph_model


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python tokens.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    token_model = token_graph_model(file_path)
    schema = graphinate.builders.GraphQLBuilder(token_model).build()
    graphinate.graphql.server(schema)
