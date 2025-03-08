from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from loguru import logger

import graphinate

DEFAULT_MAX_DEPTH = 0


def page_links_graph_model(max_depth: int = DEFAULT_MAX_DEPTH):
    """
    Create a graph model based on page links.

    Args:
        max_depth (int, optional): The maximum depth to crawl for page links. Defaults to DEFAULT_MAX_DEPTH.

    Returns:
        GraphModel: A graph model representing the page links.
    """

    def _links(url: str, depth=0, **kwargs):
        reqs = requests.get(url)
        logger.debug('Analyzing Page: {url}')
        soup = BeautifulSoup(reqs.text, 'lxml')
        logger.debug('Done Analyzing Page: {url}')
        for link in soup.find_all('a', href=True):
            child_url = link.get('href')

            if child_url.startswith('javascript:'):  # Skip JavaScript links
                continue

            if child_url.startswith('//'):  # Handle protocol-relative URLs
                child_url = f"https:{child_url}"

            if not bool(urlparse(child_url).netloc):  # Skip relative URLs
                # child_url = urljoin(url, child_url)
                continue

            if not child_url.startswith('http'):  # Skip non-HTTP URLs
                continue

            yield {'source': url, 'target': child_url}
            if depth < max_depth:
                yield from _links(child_url, depth=depth + 1, **kwargs)

    graph_model = graphinate.model(name='Web')

    @graph_model.edge()
    def link(url, **kwargs):
        yield from _links(url, **kwargs)

    return graph_model


if __name__ == '__main__':
    model = page_links_graph_model(1)

    params = {
        # 'url': 'https://github.com/erivlis/graphinate'
        'url': 'https://erivlis.github.io/graphinate/'
    }

    builder = graphinate.builders.GraphQLBuilder(model, graph_type=graphinate.GraphType.DiGraph)
    schema = builder.build(default_node_attributes={'type': 'url'}, **params)
    graphinate.graphql.server(schema)
