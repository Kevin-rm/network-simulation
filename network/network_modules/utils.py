import tkinter as tk
from tkinter import ttk, messagebox


class FormGenerator:
    def __init__(self, parent, x, y, title, fields):
        self.__x = None
        self.__y = None

        self.parent = parent
        self.set_positions(x, y)
        self.title = title
        self.fields = fields

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent):
        if not isinstance(parent, tk.Tk):
            raise ValueError("Le parent doit être une instance de tkinter.Tk")

        self.__parent = parent

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        if not isinstance(title, str):
            raise TypeError("Le title du formulaire doit être une chaîne de caractères")

        self.__title = title

    @property
    def fields(self):
        return self.__fields

    @fields.setter
    def fields(self, fields):
        for field in fields:
            if not isinstance(field, tuple) or len(field) != 2 or not isinstance(field[0], str) or field[1] not in [
                'entry', 'textarea', 'combobox'
            ]:
                raise TypeError("Chaque champ doit être un tuple (label, type de \"form-control\")")

        self.__fields = fields

    def get_positions(self):
        return self.__x, self.__y

    def set_positions(self, x, y):
        self.__x = x
        self.__y = y

    def build_form(self, validation_callback, combobox_options=None):
        form = tk.Toplevel(self.__parent)
        form.title(self.__title)
        form.attributes("-topmost", True)
        form.resizable(False, False)
        form.geometry(f"+{self.__x}+{self.__y}")

        form_frame = ttk.Frame(form, padding="5 5 5 5")
        form_frame.grid(column=0, row=0, sticky="nsew")

        row_index = 0
        form_controls = {}

        for label, form_control_type in self.__fields:
            ttk.Label(form_frame, text=f"{label} :").grid(row=row_index, column=0, sticky="w")

            form_control = None
            if form_control_type == 'entry':
                form_control = ttk.Entry(form_frame)
            elif form_control_type == 'textarea':
                form_control = tk.Text(form_frame, height=4, width=25)
            elif form_control_type == 'combobox':
                form_control = ttk.Combobox(form_frame, state="readonly")
                form_control["values"] = combobox_options

            form_control.grid(row=row_index, column=1)
            form_controls[label] = form_control
            row_index += 1

        def validate():
            try:
                validation_callback(form_controls)
                form.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        form.bind('<Return>', lambda event: validate())
        ttk.Button(form_frame, text="Valider", command=validate).grid(row=row_index, column=0, columnspan=2,
                                                                      sticky='ew')

        for child in form_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.__parent.wait_window(form)
