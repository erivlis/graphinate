from urllib.parse import urljoin, urlparse

import graphinate
import requests
from bs4 import BeautifulSoup
from loguru import logger

DEFAULT_MAX_DEPTH = 0


def page_links_graph_model(max_depth: int = DEFAULT_MAX_DEPTH):
    def _links(url: str, depth=0, **kwargs):
        reqs = requests.get(url)
        logger.debug('Analyzing Page: {url}')
        soup = BeautifulSoup(reqs.text, 'lxml')
        logger.debug('Done Analyzing Page: {url}')
        for link in soup.find_all('a', href=True):
            child_url = link.get('href')

            if child_url.startswith('//'):
                child_url = f"https:{child_url}"
            elif not bool(urlparse(child_url).netloc):
                child_url = urljoin(url, child_url)
            elif not child_url.startswith('http'):
                continue

            yield {'source': url, 'target': child_url}
            if depth < max_depth:
                yield from _links(child_url, depth=depth + 1, **kwargs)

    graph_model = graphinate.GraphModel(name='Web')

    @graph_model.edge()
    def link(url, **kwargs):
        yield from _links(url, **kwargs)

    return graph_model


if __name__ == '__main__':
    model = page_links_graph_model(1)

    params = {
        'url': 'https://github.com/erivlis/graphinate'
    }

    graphinate.materialize(
        model=model,
        graph_type=graphinate.GraphType.DiGraph,
        default_node_attributes={'type': 'url'},
        **params
    )
