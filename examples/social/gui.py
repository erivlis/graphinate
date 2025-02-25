import platform
import tkinter as tk
from tkinter import ttk


class ModalWindow(tk.Tk):
    def __init__(self, title: str):
        super().__init__()
        self.title(title)
        self.configure_window()

    def configure_window(self):
        if platform.system().lower() == 'windows':
            self.wm_attributes('-toolwindow', 'True')
        self.wm_attributes('-topmost', 'True')
        self.resizable(False, False)


class RadiobuttonChooser(ModalWindow):
    """
    Usage Example:
    ```python
    radiobutton_chooser = RadiobuttonChooser("Choose an option", {"Option 1": 1, "Option 2": 2})
    choice, value = radiobutton_chooser.get_choice()
    print(choice, value)
    ```
    """

    def __init__(self, window_title: str, options: dict, default=None):
        super().__init__(window_title)
        self.exit_button = None
        self.choice_var = tk.StringVar(self, None)
        self.default = default
        self.options = options
        self.create_widgets()
        self.mainloop()

    def create_widgets(self):
        frame = ttk.Frame(self, borderwidth=5, relief='solid')
        frame.pack(padx=4, pady=4)

        ttk.Label(frame, text="Output Mode:").pack()

        for option in self.options:
            ttk.Radiobutton(
                frame,
                text=option,
                variable=self.choice_var,
                value=option,
                command=self.enable_exit_button,
                padding=4
            ).pack(side=tk.TOP, anchor="w")

        self.exit_button = ttk.Button(self, text="OK", command=self.destroy, state=tk.DISABLED)
        self.exit_button.pack(pady=4, side=tk.BOTTOM)

    def enable_exit_button(self):
        self.exit_button['state'] = tk.NORMAL

    def get_choice(self):
        return self.choice_var.get(), self.options.get(self.choice_var.get(), self.default)


class ListboxChooser(ModalWindow):
    """
    Usage Example:

    ```python
    listbox_chooser = ListboxChooser("Choose options", {"Option 1": 1, "Option 2": 2, "Option 3": 3})
    for choice, value in listbox_chooser.get_choices():
    print(choice, value)
    ```
    """

    def __init__(self, window_title: str, options: dict, default=None):
        super().__init__(window_title)
        self.exit_button = None
        self.choices = list(options.keys())
        self.options = options
        self.default = default
        self.selection_var = tk.Variable(self)
        self.create_widgets()
        self.mainloop()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(padx=2, pady=2)

        listbox = tk.Listbox(frame, listvariable=tk.Variable(self, value=self.choices), selectmode="multiple",
                             height=min(len(self.choices), 50), width=max(len(c) for c in self.choices))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = ttk.Scrollbar(frame, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        listbox.config(yscrollcommand=scrollbar.set)

        listbox.bind("<<ListboxSelect>>", self.on_select)

        self.exit_button = ttk.Button(self, text="OK", command=self.destroy, state=tk.DISABLED)
        self.exit_button.pack(pady=4, side=tk.BOTTOM)

    def on_select(self, event):
        self.exit_button['state'] = tk.NORMAL
        self.selection_var.set(event.widget.curselection())

    def get_choices(self):
        for choice in self.selection_var.get():
            yield self.choices[choice], self.options.get(self.choices[choice], self.default)
