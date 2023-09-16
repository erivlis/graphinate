import tkinter as tk
from tkinter import ttk as ttk


def _modal_window(title: str) -> tk.Tk:
    # Creating parent Tkinter window
    win = tk.Tk()
    # win.geometry("200x125")
    win.title(title)
    win.wm_attributes('-toolwindow', 'True')
    win.wm_attributes('-topmost', 'True')
    win.resizable(False, False)
    return win


def modal_radiobutton_chooser(window_title: str, options: dict, default=None):
    # Creating parent Tkinter window
    win = _modal_window(window_title)

    # let us create a Tkinter string variable
    # that is able to store any string value
    choice_var = tk.Variable(win, None)

    radiobuttons_frame = ttk.Frame(
        win,
        borderwidth=5,
        relief='solid',
    )
    radiobuttons_frame.pack(padx=4, pady=4)

    ttk.Label(
        radiobuttons_frame,
        text="Output Mode:",
        # font=('Helvetica 9 bold'),
        # foreground="red3"
    ).pack()

    def change_state():
        exit_button['state'] = tk.NORMAL

    for option in options:
        ttk.Radiobutton(
            radiobuttons_frame,
            text=option,
            variable=choice_var,
            value=option,
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

    choice = choice_var.get()

    return choice, options.get(choice, default)


def modal_listbox_chooser(window_title: str, options: dict, default=None):
    win = _modal_window(window_title)

    choices = list(options.keys())

    choices_var = tk.Variable(win, value=choices)

    selection_var = tk.Variable(win)

    listbox_frame = ttk.Frame(
        win,
        # borderwidth=5,
        # relief='solid',
    )
    listbox_frame.pack(padx=2, pady=2)

    # Creating a Listbox and
    # attaching it to root window
    listbox = tk.Listbox(listbox_frame,
                         listvariable=choices_var,
                         selectmode="MULTIPLE",
                         height=min(len(choices), 50),
                         width=max(len(c) for c in choices))

    # Adding Listbox to the left
    # side of root window
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)

    # Creating a Scrollbar and
    # attaching it to root window
    scrollbar = tk.Scrollbar(listbox_frame)

    # Adding Scrollbar to the right
    # side of root window
    scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

    # Attaching Listbox to Scrollbar
    # Since we need to have a vertical
    # scroll we use yscrollcommand
    listbox.config(yscrollcommand=scrollbar.set)

    # setting scrollbar command parameter
    # to listbox.yview method its yview because
    # we need to have a vertical view
    scrollbar.config(command=listbox.yview)

    def on_select(e):
        print(e)
        exit_button['state'] = tk.NORMAL
        selection_var.set(listbox.curselection())

    listbox.bind("<<ListboxSelect>>", on_select)
    # listbox.bind("<Double-1>", lambda e: selection_var.set(listbox.curselection()))

    exit_button = ttk.Button(win, text="OK", command=win.destroy, state=tk.DISABLED)
    exit_button.pack(pady=4, side=tk.BOTTOM)

    win.mainloop()

    for choice in selection_var.get():
        yield choice, options.get(choices[choice], default)
        # choice = options.get(options.keys()[listbox.curselection()], default)

    # return choice, options.get(choice, default)
