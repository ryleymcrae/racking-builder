from typing import Dict

from customtkinter import (
    CTkButton,
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkOptionMenu,
    CTkScrollableFrame,
    CTkTabview,
)

from data_manager import DataManager
from enums import *


class TabView(CTkTabview):
    _tab_names = ["Inputs", "Rows", "Results"]

    def __init__(self, master, width=326, fg_color="transparent"):
        """Initialize the TabView with tabs and associated frames."""
        super().__init__(master=master, width=width, fg_color=fg_color)
        self.grid(row=0, column=0, sticky="nsew")

        # Configure each tab
        for tab_name in self._tab_names:
            self.add(tab_name)
            self.tab(tab_name).grid_rowconfigure(0, weight=1)
            self.tab(tab_name).grid_columnconfigure(0, weight=1)

        # Input frame in the first tab
        self.input_frame = CTkFrame(master=self.tab("Inputs"))
        self.input_frame.grid(row=0, column=0, pady=(10, 0), sticky="nsew")

        # Row frame in the second tab
        self.row_frame = CTkScrollableFrame(master=self.tab("Rows"), corner_radius=0)
        self.row_frame.grid(row=0, column=0, pady=(10, 0), sticky="nsew")

        self.results_frame = CTkFrame(master=self.tab("Results"))
        self.results_frame.grid(row=0, column=0, pady=(10, 0), sticky="nsew")
        self.results_frame.grid_columnconfigure(1, weight=1)

        CTkLabel(self.results_frame, text="Nothing to show yet").pack(pady=(10, 0))

    def get_input_frame(self):
        """Return the input frame for external use."""
        return self.input_frame

    def get_row_frame(self):
        """Return the row frame for external use."""
        return self.row_frame

    def get_results_frame(self):
        """Return the results frame for external use."""
        return self.results_frame


class InputFields:
    def __init__(self, parent, fields):
        self.parent = parent
        self.inputs: Dict[str, InputField] = {}
        self.data_manager = DataManager()
        self.create_input_fields(fields)

    def create_input_fields(self, fields):
        """Dynamically creates InputField instances based on provided fields data."""
        for key, (field_type, default_value, units, valid_range) in fields.items():
            label = CTkLabel(self.parent, text=key.replace("_", " ").capitalize())
            if issubclass(
                field_type, Enum
            ):  # If it's an option field, use CTkOptionMenu
                input_widget = CTkOptionMenu(
                    self.parent, values=[str(e) for e in field_type]
                )
            elif field_type is str:
                input_widget = CTkOptionMenu(self.parent, values=["Default"])
            else:  # Otherwise, use CTkEntry for numeric input
                input_widget = CTkEntry(self.parent)
            units_label = CTkLabel(self.parent, text=units) if units else None
            self.inputs[key] = InputField(
                label, input_widget, default_value, field_type, units_label, valid_range
            )

    def create_input_widgets(self, label, starting_row=0):
        """Creates all input widgets and sets them in the parent frame."""
        CTkLabel(self.parent, text=label).grid(
            row=starting_row,
            column=0,
            columnspan=3,
            pady=0 if starting_row == 0 else (16, 0),
            sticky="ew",
        )
        CTkFrame(self.parent, height=2).grid(
            row=starting_row + 1,
            column=0,
            columnspan=3,
            padx=8,
            pady=(0, 4),
            sticky="nsew",
        )
        for idx, (key, field) in enumerate(self.inputs.items()):
            field.grid(row=idx + starting_row + 2)

    def get_input(self, field_name: str):
        """Get the value of a specific input field."""
        return self.inputs[field_name].get()

    def get_input_valid_range(self, field_name: str):
        """Get the valid range of a specific input field."""
        return self.inputs[field_name].get_valid_range()

    def get_input_variable_type(self, field_name: str):
        """Get the variable type of a specific input field."""
        return self.inputs[field_name].get_variable_type()

    def restore_default_values(self):
        for input_field in self.inputs.values():
            input_field.restore_default_value()


class InputField:
    def __init__(
        self,
        label,
        input_widget: CTkEntry | CTkOptionMenu,
        default_value,
        variable_type,
        units_label=None,
        valid_range=None,
    ):
        self.label = label
        self.input_widget = input_widget
        self.default_value = default_value
        self.variable_type = variable_type
        self.units_label = units_label
        self.valid_range = valid_range
        self.restore_default_value()
        self.input_widget.configure(width=168)

    def grid(self, row):
        self.label.grid(row=row, column=0, padx=8, pady=4, sticky="w")
        self.input_widget.grid(row=row, column=1, padx=8, pady=4, sticky="w")
        if self.units_label:
            self.units_label.grid(row=row, column=2, padx=8, pady=4, sticky="ew")

    def get(self):
        return self.input_widget.get()

    def get_valid_range(self):
        return self.valid_range

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

    def restore_default_value(self):
        self.set(self.default_value)

    def get_variable_type(self):
        return self.variable_type


# Modify PanelFields to pass new field data structure to InputFields
class PanelInputFields(InputFields):
    # Passed to parent class and processed to create InputField instances
    _fields = {
        "panel_model": (str, "-- Select Panel --", None, None),
        "panel_width": (float, "", "in.", (20, 60)),
        "panel_height": (float, "", "in.", (40, 100)),
    }

    def __init__(self, parent):
        super().__init__(parent, self._fields)
        self.inputs["panel_model"].input_widget.configure(
            command=lambda e: self.set_panel_dimensions(e)
        )
        self.load_panel_models()

    def set_panel_dimensions(self, panel_model: str):
        """Set the dimensions of the panel based on the selected model."""
        panel_models = self.data_manager.get_panel_models()
        panel_names = [panel["name"] for panel in panel_models]
        for i in range(len(panel_names)):
            if panel_names[i] == panel_model:
                self.inputs["panel_height"].set(
                    panel_models[i]["height"], True, self.parent
                )
                self.inputs["panel_width"].set(
                    panel_models[i]["width"], True, self.parent
                )

    def create_input_widgets(self, starting_row=0):
        return super().create_input_widgets("Panel Specifications", starting_row)

    def load_panel_models(self, reset_selection=False):
        # Fetch panel models from data manager
        panel_names = [panel["name"] for panel in self.data_manager.get_panel_models()]

        # Update the OptionMenu's values
        self.inputs["panel_model"].input_widget.configure(values=panel_names)

        if reset_selection and panel_names:

            def update_widgets():
                first_panel = self.data_manager.get_panel_models()[0]
                self.inputs["panel_model"].default_value = first_panel["name"]
                self.inputs["panel_model"].set(first_panel["name"])
                self.inputs["panel_height"].default_value = first_panel["height"]
                self.inputs["panel_height"].set(first_panel["height"])
                self.inputs["panel_width"].default_value = first_panel["width"]
                self.inputs["panel_width"].set(first_panel["width"])

            self.parent.after(0, update_widgets)


# Modify RackingFields to pass new field data structure to InputFields
class RackingInputFields(InputFields):
    # Passed to parent class and processed to create InputField instances
    _fields = {
        "pattern": (RackingPattern, str(RackingPattern.CONTINUOUS), None, None),
        "rafter_spacing": (RafterSpacing, str(RafterSpacing.SIXTEEN), "in.", None),
        "panel_spacing": (float, 0.625, "in.", (0.39, 0.7)),
        "bracket_inset": (float, 10, "in.", (4, 16)),
        "rail_protrusion": (float, 4, "in.", (2, 6)),
    }

    def __init__(self, parent):
        super().__init__(parent, self._fields)

    def create_input_widgets(self, starting_row=0):
        return super().create_input_widgets("Racking Specifications", starting_row)


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
        return (self.entry.get(), self.orientation.get())
