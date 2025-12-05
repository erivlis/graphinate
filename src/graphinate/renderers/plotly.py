import networkx as nx
import plotly.graph_objects as go
from dash import Dash, dcc, html


def to_plotly_figure(graph: nx.Graph, with_node_labels: bool = True, with_edge_labels: bool = False):
    """
    Converts a networkx graph to a plotly figure.

    Args:
        graph (nx.Graph): The input graph to be converted.
        with_node_labels (bool): Whether to include node labels. Default is True.
        with_edge_labels (bool): Whether to include edge labels. Default is False.

    Returns:
        go.Figure: The converted plotly figure.
    """
    pos = nx.spring_layout(graph)

    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line={'width': 0.5, 'color': '#888'},
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        if with_node_labels:
            node_text.append(graph.nodes[node].get('label', str(node)))

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text' if with_node_labels else 'markers',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker={
            'showscale': True,
            'colorscale': 'YlGnBu',
            'size': 10,
            'colorbar': {
                'thickness': 15,
                'title': 'Node Connections',
                'xanchor': 'left',
                'titleside': 'right'
            }
        }
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=graph.name,
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin={'b': 20, 'l': 5, 'r': 5, 't': 40},
            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False}
        )
    )
    return fig


def plot(graph: nx.Graph, with_node_labels: bool = True, with_edge_labels: bool = False):
    """
    Plots the given networkx graph using plotly.

    Args:
        graph (nx.Graph): The input graph to be plotted.
        with_node_labels (bool): Whether to display node labels. Default is True.
        with_edge_labels (bool): Whether to display edge labels. Default is False.
    """
    fig = to_plotly_figure(graph, with_node_labels, with_edge_labels)
    fig.show()


def app(graph: nx.Graph, with_node_labels: bool = True, with_edge_labels: bool = False):
    """
    Runs a dash app to display the graph.

    Args:
        graph (nx.Graph): The input graph to be displayed.
        with_node_labels (bool): Whether to display node labels. Default is True.
        with_edge_labels (bool): Whether to display edge labels. Default is False.
    """
    app = Dash(__name__)
    fig = to_plotly_figure(graph, with_node_labels, with_edge_labels)
    app.layout = html.Div([
        dcc.Graph(figure=fig)
    ])
    app.run_server(debug=True)
