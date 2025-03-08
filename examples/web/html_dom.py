import base64

import requests
from bs4 import BeautifulSoup, Tag

import graphinate


def load_html_from_url(url="https://www.google.com"):
    response = requests.get(url)
    return response.text


def load_html(file_path):
    with open(file_path) as file:
        return file.read()


def html_dom_graph_model(html_content):
    graph_model = graphinate.model(name="HTML DOM Graph")
    soup = BeautifulSoup(html_content, 'html.parser')

    def node_type(tag: Tag):
        return tag.name.strip('[]')

    def node_key(tag: Tag):
        return str((tag.sourceline, tag.sourcepos)) if isinstance(tag, Tag) else base64.b64encode(
            tag.encode()).decode()

    def node_label(tag: Tag):
        return str(tag)

    @graph_model.node(node_type, key=node_key, label=node_label)
    def html_node():
        for tag in soup.descendants:
            if tag.name is not None:
                yield tag

    @graph_model.edge()
    def contains():
        for tag in soup.descendants:
            if tag.name is not None:
                for child in tag.children:
                    if child.name is not None:
                        yield {
                            'source': node_key(tag),
                            'target': node_key(child)
                        }

    return graph_model


if __name__ == '__main__':
    html_content = load_html_from_url()
    dom_model = html_dom_graph_model(html_content)
    schema = graphinate.builders.GraphQLBuilder(dom_model).build()
    graphinate.graphql.server(schema)
