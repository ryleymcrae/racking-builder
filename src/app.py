from customtkinter import CTk, CTkButton, CTkFrame, CTkScrollableFrame, CTkTabview

from controller import update_preview_frame
from ui import InputFields, RowFields
from utils import get_icon_path


class App(CTk):
    TITLE = "Racking Builder"
    WIDTH = 900
    HEIGHT = 600

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.configure_root()
        self.input_fields = None
        self.row_fields = None
        self.build_ui()
        self.init_inputs()
        self.init_row_builder()

    def configure_root(self):
        """Configure root window properties."""
        self.title(self.TITLE)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(self.WIDTH, self.HEIGHT)
        self.resizable(True, False)
        self.iconbitmap(get_icon_path())
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def build_ui(self):
        """Set up the basic UI structure: sidebar with a tabview, input frame, row builder, and preview frame."""
        # Sidebar
        self.sidebar = CTkFrame(master=self, corner_radius=0)
        self.sidebar.grid_rowconfigure(0, weight=1)
        self.sidebar.grid(row=0, column=0, sticky="nsew")  # Sidebar gridding

        # Create a Tabview for the sidebar
        self.tabview = CTkTabview(
            master=self.sidebar, fg_color="transparent", width=343
        )
        self.tabview.grid(row=0, column=0, sticky="nsew")

        # Adding tabs to the tabview
        self.tabview.add("Array Information")
        self.tabview.add("Rows")
        # Configure each tab
        self.tabview.tab("Array Information").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Array Information").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Rows").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Rows").grid_columnconfigure(0, weight=1)

        # Input frame in the first tab
        self.input_frame = CTkFrame(master=self.tabview.tab("Array Information"))
        self.input_frame.grid(row=0, column=0, pady=(10, 0), sticky="nsew")

        # Row frame in the second tab
        self.row_frame = CTkScrollableFrame(
            master=self.tabview.tab("Rows"), corner_radius=0
        )
        self.row_frame.grid(row=0, column=0, pady=(10, 0), sticky="nsew")

        # Refresh button outside the tabview, below it
        self.calculate_and_preview_button = CTkButton(
            master=self.sidebar,
            text="Calculate & Preview",
            corner_radius=0,
            command=self.calculate_and_preview,
        )
        self.calculate_and_preview_button.grid(row=1, column=0, sticky="ew")

        # Preview Frame
        self.preview_frame = CTkScrollableFrame(master=self, fg_color="transparent")
        self.preview_frame.grid(row=0, column=1, sticky="nsew")

    def init_inputs(self):
        """Initialize the input fields for panel settings."""
        self.input_fields = InputFields(self.input_frame)
        self.input_fields.create_input_widgets()
        # Set default values
        default_inputs = self.input_fields.default_inputs
        print(default_inputs)
        for key, input_field in self.input_fields.inputs.items():
            print(key)
            if default_inputs.get(key):
                input_field.set(default_inputs.get(key))

    def init_row_builder(self):
        """Initialize the row builder with add/remove row functionality."""
        self.row_fields = RowFields(self.row_frame)
        self.row_fields.init_row_controls()

    def calculate_and_preview(self):
        """Needs summary"""
        try:
            # Define the fields that should be checked for emptiness and negativity
            fields_to_check = {
                "panel_width": float,
                "panel_height": float,
                "first_bracket_inset": float,
                "rafter_spacing": int
            }

            # Check each field for empty input and ensure it's non-negative
            for field_name, cast_type in fields_to_check.items():
                value = self.input_fields.get_input(field_name).strip()

                # Check if the input is empty
                if value == "":
                    raise ValueError(f"{field_name.replace('_', ' ').capitalize()} cannot be empty.")

                # Parse the input to the correct type (float/int) and check if it's negative
                numeric_value = cast_type(value)
                if numeric_value < 0:
                    raise ValueError(f"{field_name.replace('_', ' ').capitalize()} cannot be negative.")

            # All inputs are valid, continue with the rest of the logic
            panel_width = float(self.input_fields.get_input("panel_width"))
            panel_height = float(self.input_fields.get_input("panel_height"))
            inset = float(self.input_fields.get_input("first_bracket_inset"))
            rafter_spacing = int(self.input_fields.get_input("rafter_spacing"))
            
        except ValueError as e:
            self.tabview.set("Array Information")
            return self.show_warning_dialog(str(e))
        
        try:
            row_data = self.row_fields.get_row_data()
        except ValueError as e:
            self.tabview.set("Rows")
            return self.show_warning_dialog(str(e))
            
        update_preview_frame(self.preview_frame, row_data, panel_width, panel_height)

    def show_warning_dialog(self, message):
        from tkinter import messagebox

        messagebox.showwarning("Invalid Input", message)


if __name__ == "__main__":
    app = App()
    app.mainloop()
