import networkx as nx

import graphinate
import graphinate.tools.gui


def get_graph():
    options = {
        'Tetrahedron': nx.tetrahedral_graph(),
        'Cube': nx.hypercube_graph(3),
        'Octahedron': nx.octahedral_graph(),
        'Icosahedron': nx.icosahedral_graph(),
        'Dodechedron': nx.dodecahedral_graph(),
        'Tesseract': nx.hypercube_graph(4),
        'Truncated Cube': nx.truncated_cube_graph(),
        'Truncated Tetrahedron': nx.truncated_tetrahedron_graph()
    }

    return graphinate.tools.gui.modal_radiobutton_chooser('Choose Graph', options)


def model():
    name, graph = get_graph()
    graph_model = graphinate.GraphModel(name)

    @graph_model.edge()
    def edge():
        for edge in graph.edges:
            yield {'source': edge[0], 'target': edge[1]}

    return graph_model


if __name__ == '__main__':
    model = model()
    graphinate.materialize(model.name, model)
