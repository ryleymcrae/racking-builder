from enum import Enum
from typing import Tuple, Dict
import sys
import os

from customtkinter import (
    BOTH,
    BOTTOM,
    LEFT,
    RIGHT,
    TOP,
    CTk,
    CTkButton,
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkOptionMenu,
    CTkScrollableFrame,
    X,
    ThemeManager
)
from tkinter import messagebox

def get_icon_path():
    if getattr(sys, 'frozen', False):  # If running as a bundled executable
        application_path = sys._MEIPASS  # Path where PyInstaller extracts files
        return os.path.join(application_path, "icon.ico")
    else:
        return "icon.ico"  # Path when running from source


class App(CTk):
    TITLE = "Racking Builder"
    WIDTH = 900
    HEIGHT = 600

    def __init__(self, fg_color: str | Tuple[str, str] | None = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.configure_root()
        self.build_ui()
        self.init_inputs()
        self.init_row_builder()

    def configure_root(self):
        self.title(self.TITLE)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(self.WIDTH, self.HEIGHT)
        self.resizable(True, False)
        self.iconbitmap(get_icon_path())
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def init_inputs(self):
        def set_panel_dimensions(panel_name):
            """Set the dimensions of the panel based on the selected model."""
            panel = PanelType.map()[panel_name]
            width = panel.width_inches
            height = panel.height_inches
            self.inputs["panel_width"].set(round(width, 4) if width else "", notify=True, root=self)
            self.inputs["panel_height"].set(round(height, 4) if height else "", notify=True, root=self)

        self.inputs: Dict[str, InputField] = {
            "panel_model": InputField(
                label=CTkLabel(self.input_frame, text="Panel Model"),
                input_widget=CTkOptionMenu(
                    self.input_frame, values=[panel.name for panel in PanelType], command=lambda e: set_panel_dimensions(e)
                ),
                units_label=None,
            ),
            "panel_height": InputField(
                label=CTkLabel(self.input_frame, text="Panel Height"),
                input_widget=CTkEntry(self.input_frame),
                units_label=CTkLabel(self.input_frame, text="Inches"),
            ),
            "panel_width": InputField(
                label=CTkLabel(self.input_frame, text="Panel Width"),
                input_widget=CTkEntry(self.input_frame),
                units_label=CTkLabel(self.input_frame, text="Inches"),
            ),
            "pattern": InputField(
                label=CTkLabel(self.input_frame, text="Mounting Pattern"),
                input_widget=CTkOptionMenu(
                    self.input_frame, values=["Continuous", "Staggered"]
                ),
                units_label=None,
            ),
            "inset": InputField(
                label=CTkLabel(self.input_frame, text="First Bracket Inset"),
                input_widget=CTkEntry(self.input_frame),
                units_label=CTkLabel(self.input_frame, text="Inches"),
            ),
            "rafter_spacing": InputField(
                label=CTkLabel(self.input_frame, text="Rafter Spacing"),
                input_widget=CTkOptionMenu(self.input_frame, values=["12", "18", "24", "32", "48"]),
                units_label=CTkLabel(self.input_frame, text="Inches"),
            ),
        }

        for id, (key, input_field) in enumerate(self.inputs.items()):
            input_field.grid(row=id)

    def init_row_builder(self):
        def add_row():
            row_field = RowField(entry_frame)
            row_field.grid(len(self.rows))
            self.rows.append(row_field)

        def delete_row():
            if len(self.rows) <= 1:
                return
            row_field = self.rows.pop()
            row_field.grid_forget()

        self.row_frame.grid_rowconfigure(0, weight=1)
        delete_row_button = CTkButton(self.row_frame, text="Delete Row", command=delete_row)
        delete_row_button.grid(row=0, column=0, padx=(0, 4), pady=8, sticky="ew")
        add_row_button = CTkButton(self.row_frame, text="Add Row", command=add_row)
        add_row_button.grid(row=0, column=1, padx=4, pady=8, sticky="ew")
        entry_frame = CTkFrame(self.row_frame, corner_radius=0, fg_color="transparent")
        entry_frame.grid(row=1, columnspan=2, sticky="nsew")
        self.rows = []
        add_row()

    def build_ui(self):
        # Sidebar
        self.sidebar = CTkFrame(master=self, width=300, corner_radius=0)
        self.sidebar.grid_rowconfigure(1, weight=1)
        self.input_frame: CTkFrame = CTkFrame(master=self.sidebar)
        self.row_frame: CTkFrame = CTkScrollableFrame(master=self.sidebar)
        self.refresh_button: CTkButton = CTkButton(
            master=self.sidebar, text="Calculate & Preview", command=self.update_outputs
        )
        # Preview Frame
        self.preview_frame: CTkScrollableFrame = CTkScrollableFrame(master=self, fg_color="transparent")
        # Place widgets
        self.sidebar.grid(row=0, column=0, padx=(0, 4), sticky="ns")
        self.input_frame.grid(row=0, column=0, padx=4, pady=(4, 0))
        self.row_frame.grid(row=1, column=0, padx=(4, 5), pady=4, sticky="nsew")
        self.refresh_button.grid(row=2, column=0, padx=4, pady=(0, 4), sticky="ew")
        self.preview_frame.grid(row=0, column=1, sticky="nsew")

    def update_outputs(self):
        def foo(row_data):
            panel = PanelType.map()[self.inputs["panel_model"].get()]
            for child in self.preview_frame.winfo_children():
                child.grid_forget()
            for id, (num_panels, orientation) in enumerate(row_data):
                row_frame = CTkFrame(self.preview_frame, fg_color="transparent")
                row_frame.grid(row=id, column=0, sticky="nsew")
                for i in range(num_panels):
                    width, height = (panel.width_inches, panel.height_inches) if orientation == "Portrait" else (panel.height_inches, panel.width_inches)
                    CTkFrame(row_frame, width=width, height=height, fg_color="black", corner_radius=0, border_width=1).grid(row=id, column=i, padx=0.625, pady=0.625, sticky="nsew")
        
        row_data = []
        try:
            for row_field in self.rows:
                num_panels, orientation = row_field.get()
                row_data.append((num_panels, orientation))
            foo(row_data)
        except ValueError as e:
            messagebox.showwarning("Invalid Input", str(e))


class InputField:
    def __init__(
        self, label: CTkLabel, input_widget: CTkEntry | CTkOptionMenu, units_label: CTkLabel
    ):
        self.label = label
        self.input_widget = input_widget
        self.units_label = units_label

    def grid(self, row):
        """Place the label and input widget in the specified grid position."""
        pady = (4, 10) if row == 5 else 4 if row else (10, 4)  # Extra top padding for top row
        self.label.grid(row=row, column=0, padx=8, pady=pady, sticky="w")
        self.input_widget.grid(row=row, column=1, padx=8, pady=pady, sticky="ew")
        if self.units_label:
            self.units_label.grid(row=row, column=2, padx=8, pady=pady, sticky="ew")

    def get(self) -> str:
        """Return the current value of the input widget."""
        return self.input_widget.get()

    def get_label(self) -> str:
        """Return the label text associated with the input widget."""
        return self.label._text

    def set(self, new_value, notify=False, root=None) -> None:
        """Set a new value to the input widget."""
        self.input_widget.delete(0, "end")  # Clear existing value
        self.input_widget.insert(0, new_value)
        if notify and root:
            self.input_widget.configure(border_color=("#2CC985", "#2FA572"))
            root.after(
                750,
                lambda: self.input_widget.configure(
                    border_color=ThemeManager.theme["CTkEntry"]["border_color"]
                ),
            )

class RowField:
    def __init__(self, parent):
        self.entry = CTkEntry(parent)
        self.orientation = CTkOptionMenu(parent, values=["Portrait", "Landscape"])

    def grid(self, row):
        self.row = row
        pady = (4, 2) if row == 0 else 4
        self.entry.grid(row=row, column=1, padx=4, pady=pady)
        self.orientation.grid(row=row, column=2, padx=(0, 4), pady=pady)

    def grid_forget(self):
        self.entry.grid_forget()
        self.orientation.grid_forget()

    def get(self):
        if self.entry.get() == "":
            raise ValueError(f"The value for row {self.row+1} is blank.")
        try:
            num_panels = int(self.entry.get())
            orientation = self.orientation.get()
            return num_panels, orientation
        except ValueError:
            raise ValueError(f"The value for row {self.row+1} is invalid. Please enter a valid `int`.")

class PanelType(Enum):
    CUSTOM = ("Custom", None, None)
    LONGI505 = ("LONGi 505W", 2094, 1134)

    def __init__(self, *values) -> None:
        self.values = values

    @property
    def name(self) -> str:
        return self.values[0]

    @property
    def height_inches(self) -> float:
        return self.values[1] / 25.4 if self.values[1] else None

    @property
    def width_inches(self) -> float:
        return self.values[2] / 25.4 if self.values[2] else None

    @classmethod
    def map(cls):
        return {panel.name: panel for panel in cls}

if __name__ == "__main__":
    app = App()
    app.mainloop()
