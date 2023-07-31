import tkinter as tk
import tkinter.ttk as ttk
from pprint import pprint

from . import builders, server
from .modeling import GraphModel
from .plot import show

output_modes = {
    'NetworkX': (builders.NetworkxBuilder, show),
    'D3 Graph': (builders.D3Builder, pprint),
    'Generic GraphQL': (builders.GenericGraphQLBuilder, server.run_graphql),
    'Typed GraphQL': (builders.TypedGraphQLBuilder, server.run_graphql)
}


def gui_mode_chooser(title: str):
    # Creating parent Tkinter window
    win = tk.Tk()
    # win.geometry("200x125")
    win.title(title)
    win.wm_attributes('-toolwindow', 'True')
    win.wm_attributes('-topmost', 'True')
    win.resizable(False, False)

    # let us create a Tkinter string variable
    # that is able to store any string value
    mode_var = tk.Variable(win, None)

    # here is a Dictionary to create multiple buttons
    options = {k: k for k in output_modes.keys()}

    mode_radiobuttons_frame = ttk.Frame(
        win,
        borderwidth=5,
        relief='solid',
    )
    mode_radiobuttons_frame.pack(padx=4, pady=4)

    ttk.Label(
        mode_radiobuttons_frame,
        text="Output Mode:",
        # font=('Helvetica 9 bold'),
        # foreground="red3"
    ).pack()

    def change_state():
        exit_button['state'] = tk.NORMAL

    for (txt, val) in options.items():
        ttk.Radiobutton(
            mode_radiobuttons_frame,
            text=txt,
            variable=mode_var,
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

    # sv_ttk.set_theme("dark")

    win.mainloop()

    return mode_var.get()


def materialize(title: str,
                graph_model: GraphModel,
                graph_type: builders.GraphType = builders.GraphType.Graph,
                **kwargs):
    if mode := gui_mode_chooser(title):
        builder, show = output_modes.get(mode, (None, None))
        if builder:
            materialized_graph = builders.build(builder, graph_model, graph_type, **kwargs)
            show(materialized_graph)
