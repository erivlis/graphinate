import tkinter as tk
import tkinter.ttk as ttk

import sv_ttk

from .modeling import GraphModel
from .builders import D3Builder, GraphQLBuilder, SimpleGraphQLBuilder, NetworkxBuilder


def _d3(graph_model, **kwargs):
    d3_graph = D3Builder(graph_model)
    d3_dict = d3_graph.build(**kwargs)

    from pprint import pprint
    pprint(d3_dict)


def _graphql_server(graphql_schema):
    import uvicorn
    from starlette.applications import Starlette
    from strawberry.asgi import GraphQL
    import webbrowser

    port = 8000

    def open_url():
        webbrowser.open(f'http://localhost:{port}/graphql')

    graphql_app = GraphQL(graphql_schema)
    app = Starlette(on_startup=[open_url])
    app.add_route("/graphql", graphql_app)
    app.add_websocket_route("/graphql", graphql_app)

    uvicorn.run(app, host='0.0.0.0', port=port)


def _graphql(graph_model, **kwargs):
    gql_graph = GraphQLBuilder(graph_model)
    graphql_schema = gql_graph.build(**kwargs)

    _graphql_server(graphql_schema)


def _simple_graphql(graph_model, **kwargs):
    gql_graph = SimpleGraphQLBuilder(graph_model)
    graphql_schema = gql_graph.build(**kwargs)

    _graphql_server(graphql_schema)


def _networkx(graph_model, **kwargs):
    import networkx as nx
    from graphinate.plot import show

    # NetworkX Graph
    networkx_graph = NetworkxBuilder(graph_model)
    nx_graph: nx.Graph = networkx_graph.build(**kwargs)

    show(nx_graph)


output_modes = {
    'NetworkX': _networkx,
    'D3 Graph': _d3,
    'GraphQL': _graphql,
    'Simple GraphQL': _simple_graphql
}


def choose_mode(title: str):
    # Creating parent Tkinter window
    win = tk.Tk()
    # win.geometry("200x125")
    win.title(title)
    win.wm_attributes('-toolwindow', 'True')
    win.resizable(False, False)

    # let us create a Tkinter string variable
    # that is able to store any string value
    v = tk.StringVar(win, "")

    # here is a Dictionary to create multiple buttons
    options = {k: k for k in output_modes.keys()}

    def change_state():
        exit_button['state'] = tk.NORMAL

    frame = ttk.Frame(
        win,
        borderwidth=5,
        relief='solid',
    )
    frame.pack(padx=4, pady=4)

    label = ttk.Label(
        frame,
        text="Output Mode:",
        # font=('Helvetica 9 bold'),
        # foreground="red3"
    )
    label.pack()

    # We will use a Loop just to create multiple
    # Radiobuttons instead of creating each button separately
    for (txt, val) in options.items():
        ttk.Radiobutton(
            frame,
            text=txt,
            variable=v,
            value=val,
            command=change_state,
            padding=4
        ).pack(
            side=tk.TOP,
            # ipady=1,
            anchor="w"
        )

    exit_button = ttk.Button(win, text="OK", command=win.destroy, state=tk.DISABLED)
    exit_button.pack(pady=4, side=tk.BOTTOM)

    sv_ttk.set_theme("dark")

    win.mainloop()

    return v.get()


def display(title: str, graph_model: GraphModel, **kwargs):
    mode = str(choose_mode(title))
    if output_mode := output_modes.get(mode, None):
        output_mode(graph_model, **kwargs)
