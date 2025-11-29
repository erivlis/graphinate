import itertools
import string
import urllib.request
from collections.abc import Iterable

import graphinate


def word_model(title: str, words: Iterable[str]) -> graphinate.GraphModel:
    graph_model = graphinate.model(name=title)

    @graph_model.edge()
    def edge():
        for w1, w2 in itertools.pairwise(words):
            yield {'source': w1, 'target': w2}

    return graph_model


def words(url: str):
    data = urllib.request.urlopen(url)
    for line in data:  # files are iterable
        for w in line.decode().strip().split():
            word = w.strip().lower().translate(str.maketrans('', '', string.punctuation))
            yield word


if __name__ == '__main__':
    great_expectations = 'https://www.gutenberg.org/cache/epub/1400/pg1400.txt'
    moby_dick = 'https://www.gutenberg.org/cache/epub/2701/pg2701.txt'
    alice_in_wonderland = 'https://www.gutenberg.org/cache/epub/11/pg11.txt'

    model = word_model('alice_in_wonderland', itertools.islice(words(alice_in_wonderland), 5000))
    builder = graphinate.builders.GraphQLBuilder(model)

    # to create a Strawberry GraphQL schema
    schema = builder.build()

    # and serve it using Uvicorn web server
    graphinate.graphql.server(schema)
