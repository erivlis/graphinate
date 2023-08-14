"""
pip install beautifulsoup4
pip install lxml
pip install requests
"""
from urllib.parse import urlparse, urljoin

import networkx as nx
import requests
from bs4 import BeautifulSoup

import graphinate.builders
from graphinate.materialize.matplotlib import show

DEPTH = 0


def _links(url: str, depth=0, **kwargs):
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'lxml')
    for link in soup.find_all('a', href=True):
        child_url = link.get('href')

        if child_url.startswith('//'):
            child_url = f"https:{child_url}"
        elif not bool(urlparse(child_url).netloc):
            child_url = urljoin(url, child_url)
        yield {'source': url, 'target': child_url}
        if depth < DEPTH:
            yield from _links(child_url, depth=depth + 1, **kwargs)


graph_model = graphinate.GraphModel(name='Web')


@graph_model.edge()
def edges(url, **kwargs):
    yield from _links(url, **kwargs)


if __name__ == '__main__':
    networkx_graph = graphinate.builders.NetworkxBuilder(graph_model)

    # params = {
    #     'user_id': 'erivlis',
    #     'repository_id': 'graphinate',
    #     # 'user_id': 'andybrewer',
    #     # 'repository_id': 'operation-go',
    #     # 'commit_id': None,
    #     'file_id': 'README.md',
    #     # 'user_id' "strawberry-graphql"
    # }

    base_url = 'https://github.com/erivlis/graphinate'

    nx_graph: nx.Graph = networkx_graph.build(url=base_url)

    show(nx_graph)
