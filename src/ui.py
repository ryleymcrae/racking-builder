from typing import Any, Dict

from customtkinter import (
    CTkButton,
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkOptionMenu,
    CTkScrollableFrame,
    CTkTabview,
)

from enums import PanelType


class TabView(CTkTabview):
    _tab_names = ["Array Information", "Rows", "Results"]

    def __init__(self, master, width=343):
        """Initialize the TabView with tabs and associated frames."""
        super().__init__(master=master, width=width)
        self.grid(row=0, column=0, sticky="nsew")

        # Configure each tab
        for tab_name in self._tab_names:
            self.add(tab_name)
            self.tab(tab_name).grid_rowconfigure(0, weight=1)
            self.tab(tab_name).grid_columnconfigure(0, weight=1)

        # Input frame in the first tab
        self.input_frame = CTkFrame(master=self.tab("Array Information"))
        self.input_frame.grid(row=0, column=0, pady=(10, 0), sticky="nsew")

        # Row frame in the second tab
        self.row_frame = CTkScrollableFrame(master=self.tab("Rows"), corner_radius=0)
        self.row_frame.grid(row=0, column=0, pady=(10, 0), sticky="nsew")

    def get_input_frame(self):
        """Return the input frame for external use."""
        return self.input_frame

    def get_row_frame(self):
        """Return the row frame for external use."""
        return self.row_frame


class InputFields:
    def __init__(self, parent):
        self.parent = parent
        self.inputs: Dict[str, InputField] = {}

    @property
    def default_inputs(self):
        default_panel = list(PanelType)[0]  # Get the first item in the enum
        return {
            "first_bracket_inset": 10,
            "panel_width": default_panel.width_inches,
            "panel_height": default_panel.height_inches,
            "panel_spacing": 0.625,
            "rail_protrusion": 4,
        }

    def create_input_widgets(self):
        """Creates all input widgets and sets them in the parent frame."""
        panel_inputs = ["panel_model", "panel_height", "panel_width"]
        self.inputs = {
            "panel_model": InputField(
                label=CTkLabel(self.parent, text="Panel Model"),
                input_widget=CTkOptionMenu(
                    self.parent,
                    values=[panel.name for panel in PanelType],
                    command=self.set_panel_dimensions,
                ),
                units_label=None,
            ),
            "panel_width": InputField(
                label=CTkLabel(self.parent, text="Panel Width"),
                input_widget=CTkEntry(self.parent),
                units_label=CTkLabel(self.parent, text="Inches"),
            ),
            "panel_height": InputField(
                label=CTkLabel(self.parent, text="Panel Height"),
                input_widget=CTkEntry(self.parent),
                units_label=CTkLabel(self.parent, text="Inches"),
            ),
            "pattern": InputField(
                label=CTkLabel(self.parent, text="Mounting Pattern"),
                input_widget=CTkOptionMenu(
                    self.parent, values=["Continuous", "Staggered"]
                ),
                units_label=None,
            ),
            "rafter_spacing": InputField(
                label=CTkLabel(self.parent, text="Rafter Spacing"),
                input_widget=CTkOptionMenu(
                    self.parent, values=["12", "16", "19.1875", "24", "32", "48"]
                ),
                units_label=CTkLabel(self.parent, text="Inches"),
            ),
            "panel_spacing": InputField(
                label=CTkLabel(self.parent, text="Panel Spacing"),
                input_widget=CTkEntry(self.parent),
                units_label=CTkLabel(self.parent, text="Inches"),
            ),
            "first_bracket_inset": InputField(
                label=CTkLabel(self.parent, text="First Bracket Inset"),
                input_widget=CTkEntry(self.parent),
                units_label=CTkLabel(self.parent, text="Inches"),
            ),
            "rail_protrusion": InputField(
                label=CTkLabel(self.parent, text="Rail Protrusion"),
                input_widget=CTkEntry(self.parent),
                units_label=CTkLabel(self.parent, text="Inches"),
            ),
        }

        # Place all input fields with a spacer between panel inputs and other inputs
        spacer_placed = False
        for idx, (key, field) in enumerate(self.inputs.items()):
            if key in panel_inputs:
                field.grid(row=idx)
            else:
                if not spacer_placed:
                    CTkFrame(self.parent, height=2).grid(
                        row=idx, columnspan=3, padx=8, pady=4, sticky="ew"
                    )
                    spacer_placed = True
                field.grid(row=idx + 1)

    def set_panel_dimensions(self, panel_model: str):
        """Set the dimensions of the panel based on the selected model."""
        panel = PanelType.map()[panel_model]
        self.inputs["panel_height"].set(panel.height_inches, True, self.parent)
        self.inputs["panel_width"].set(panel.width_inches, True, self.parent)

    def get_input(self, field_name: str):
        """Get the value of a specific input field."""
        return self.inputs[field_name].get()


class InputField:
    def __init__(self, label, input_widget: CTkEntry | CTkOptionMenu, units_label=None):
        self.label = label
        self.input_widget = input_widget
        self.units_label = units_label

    def grid(self, row):
        self.label.grid(row=row, column=0, padx=8, pady=4, sticky="w")
        self.input_widget.grid(row=row, column=1, padx=8, pady=4, sticky="ew")
        if self.units_label:
            self.units_label.grid(row=row, column=2, padx=8, pady=4, sticky="ew")

    def get(self):
        return self.input_widget.get()

    def set(self, new_value, notify=False, parent=None) -> None:
        from customtkinter import ThemeManager

        """Set a new value to the input widget."""
        if isinstance(self.input_widget, CTkEntry):
            self.input_widget.delete(0, "end")
            self.input_widget.insert(0, new_value)
        elif isinstance(self.input_widget, CTkOptionMenu):
            self.input_widget.set(new_value)
        # Optionally notify the user by changing the input_widget border color to green
        if notify and parent:
            self.input_widget.configure(border_color=("#2CC985", "#2FA572"))
            parent.after(
                1000,
                lambda: self.input_widget.configure(
                    border_color=ThemeManager.theme["CTkEntry"]["border_color"]
                ),
            )


class RowFields:
    def __init__(self, parent):
        self.parent = parent
        self.rows = []

    def init_row_controls(self):
        """Initialize the 'Add Row' and 'Delete Row' controls."""
        add_row_button = CTkButton(self.parent, text="Add Row", command=self.add_row)
        delete_row_button = CTkButton(
            self.parent, text="Delete Row", command=self.delete_row
        )

        add_row_button.grid(row=0, column=1, padx=4, pady=8, sticky="ew")
        delete_row_button.grid(row=0, column=0, padx=(0, 4), pady=8, sticky="ew")

        self.add_row()  # Start with one row

    def add_row(self):
        """Add a new row to the row builder."""
        row = RowField(self.parent)
        self.rows.append(row)
        row.grid(len(self.rows))

    def delete_row(self):
        """Remove the last row from the row builder."""
        if len(self.rows) > 1:
            row = self.rows.pop()
            row.grid_forget()

    def get_row_data(self):
        """Get the data from all rows."""
        row_data = []
        for row in self.rows:
            row_data.append(row.get())
        return row_data


class RowField:
    def __init__(self, parent):
        self.entry = CTkEntry(parent)
        self.orientation = CTkOptionMenu(parent, values=["Portrait", "Landscape"])

    def grid(self, row):
        self.entry.grid(row=row, column=0, padx=4, pady=4)
        self.orientation.grid(row=row, column=1, padx=(0, 4), pady=4)

    def grid_forget(self):
        self.entry.grid_forget()
        self.orientation.grid_forget()

    def get(self):
        try:
            num_panels = int(self.entry.get())
            if num_panels < 1 or num_panels > 100:
                raise ValueError
            orientation = self.orientation.get()
            return num_panels, orientation
        except ValueError:
            raise ValueError(
                "An entry for a number of panels is invalid. Please ensure the values are all non-empty integers between 1 and 100"
            )
