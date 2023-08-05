import tkinter as tk
from tkinter import ttk as ttk


def modal_radiobutton_chooser(window_title: str, options: dict, default=None):
    # Creating parent Tkinter window
    win = tk.Tk()
    # win.geometry("200x125")
    win.title(window_title)
    win.wm_attributes('-toolwindow', 'True')
    win.wm_attributes('-topmost', 'True')
    win.resizable(False, False)

    # let us create a Tkinter string variable
    # that is able to store any string value
    mode_var = tk.Variable(win, None)

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

    for option in options.keys():
        ttk.Radiobutton(
            mode_radiobuttons_frame,
            text=option,
            variable=mode_var,
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

    choice = mode_var.get()

    return choice, options.get(choice, default)
