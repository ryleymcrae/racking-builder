from tkinter import messagebox

from customtkinter import CTk, CTkButton, CTkFrame, CTkScrollableFrame

from controller import edit_data, update_preview_frame, update_results
from ui import PanelInputFields, RackingInputFields, RowFields, TabView
from utils import *


class App(CTk):
    TITLE = "Racking Builder"
    WIDTH = 900
    HEIGHT = 680

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.configure_root()
        # Members
        self.input_fields = None
        self.row_fields = None
        self.tabview = None
        # Setup
        self.build_ui()
        self.init_inputs()
        self.set_default_inputs()
        self.init_row_builder()
        # self.after(250, lambda: print(self.sidebar.winfo_width()))

    def configure_root(self):
        """Configure root window properties."""
        self.title(self.TITLE)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(self.WIDTH, self.HEIGHT)
        self.resizable(False, False)
        self.iconbitmap(get_icon_path())
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def build_ui(self):
        """Set up the basic UI structure: sidebar with a tabview, input frame, row builder, and preview frame."""
        # Sidebar
        self.sidebar = CTkFrame(master=self, corner_radius=0)
        self.sidebar.grid_rowconfigure(0, weight=1)
        self.sidebar.grid(row=0, column=0, sticky="nsew")  # Sidebar gridding

        # TabView
        self.tabview = TabView(self.sidebar)
        self.tabview.grid(
            row=0, column=0, columnspan=2, sticky="nsew"
        )  # Add this line to grid it

        # Buttons
        self.edit_data_button = CTkButton(
            master=self.sidebar,
            text="Edit Data",
            corner_radius=0,
            command=lambda: edit_data(
                self.preview_frame, self.panel_fields.load_panel_models
            ),
        )
        self.edit_data_button.grid(row=1, column=0, sticky="ew")
        self.get_results_button = CTkButton(
            master=self.sidebar,
            text="Get Results",
            corner_radius=0,
            command=self.calculate_and_preview,
        )
        self.get_results_button.grid(row=1, column=1, padx=(1, 0), sticky="ew")

        # Preview Frame
        self.preview_frame = CTkScrollableFrame(master=self, fg_color="transparent")
        self.preview_frame.grid(row=0, column=1, sticky="nsew")

    def init_inputs(self):
        """Initialize the input fields for panel and racking settings."""
        # Panel Fields
        self.panel_fields = PanelInputFields(self.tabview.get_input_frame())
        self.panel_fields.create_input_widgets()

        # Racking Fields (Below the panel fields)
        self.racking_fields = RackingInputFields(self.tabview.get_input_frame())
        self.racking_fields.create_input_widgets(
            starting_row=len(self.panel_fields.inputs) + 3
        )

    def set_default_inputs(self):
        self.panel_fields.restore_default_values()
        self.racking_fields.restore_default_values()

    def init_row_builder(self):
        """Initialize the row builder with add/remove row functionality."""
        self.row_fields = RowFields(self.tabview.get_row_frame())
        self.row_fields.init_row_controls()

    def calculate_and_preview(self):
        """Collect inputs and calculate the results."""
        user_inputs = {}
        try:
            # Process inputs for both panel and racking fields
            user_inputs.update(process_fields(self.panel_fields))
            user_inputs.update(process_fields(self.racking_fields))

        except ValueError as e:
            self.tabview.set("Array Information")
            return self.show_warning_dialog("Invalid Array Input", str(e))

        user_row_data = self.row_fields.get_row_data()
        row_data = []
        try:
            for id, (num_panels, orientation) in enumerate(user_row_data):
                if num_panels == "":
                    raise ValueError(f"The value in row {id + 1} is empty.")
                n = int(num_panels)
                if n < 1 or n > 100:
                    raise ValueError(
                        f"The value in row {id + 1} is outside the valid range of [1, 100]"
                    )
                else:
                    row_data.append((n, orientation))
        except ValueError as e:
            self.tabview.set("Rows")
            return self.show_warning_dialog("Invalid Row Input", str(e))

        update_preview_frame(self.preview_frame, row_data, user_inputs)

        equipment_data = get_equipment_data(row_data, user_inputs)

        update_results(self.tabview.get_results_frame(), equipment_data)
        self.tabview.set("Results")

    def show_warning_dialog(self, title, message):
        messagebox.showwarning(title, message)


if __name__ == "__main__":
    app = App()
    app.mainloop()
