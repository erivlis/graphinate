import graphinate
from graphinate.materialize.matplotlib import show

graph_model = graphinate.model(name='Hailstone')


def h(h_id):
    if h_id % 2 == 0:
        return h_id / 2
    else:
        return 3 * h_id + 1


def hailstone(hid: int):
    pass


if __name__ == '__main__':
    networkx_graph = graphinate.builders.NetworkxBuilder(graph_model)

    params = {
        'h_id': 7
    }
    graph = networkx_graph.build(**params)
    show(graph)
