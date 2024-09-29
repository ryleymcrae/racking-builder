# app.py
from customtkinter import CTk, CTkButton, CTkFrame, CTkScrollableFrame

from controller import update_outputs
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
        """Set up the basic UI structure: sidebar, input frame, row builder, and preview frame."""
        # Sidebar
        self.sidebar = CTkFrame(master=self, corner_radius=0)
        self.sidebar.grid_rowconfigure(1, weight=1)

        # Input and row builder frames
        self.input_frame = CTkFrame(master=self.sidebar)
        self.row_frame = CTkScrollableFrame(master=self.sidebar)
        self.refresh_button = CTkButton(
            master=self.sidebar, text="Calculate & Preview", command=self.update_outputs
        )

        # Preview Frame
        self.preview_frame = CTkScrollableFrame(master=self, fg_color="transparent")

        # Place widgets
        self.sidebar.grid(row=0, column=0, padx=(0, 4), sticky="ns")
        self.input_frame.grid(row=0, column=0, padx=4, pady=(4, 0))
        self.row_frame.grid(row=1, column=0, padx=(4, 5), pady=4, sticky="nsew")
        self.refresh_button.grid(row=2, column=0, padx=4, pady=(0, 4), sticky="ew")
        self.preview_frame.grid(row=0, column=1, sticky="nsew")

    def init_inputs(self):
        """Initialize the input fields for panel settings."""
        self.input_fields = InputFields(self.input_frame)
        self.input_fields.create_input_widgets()

    def init_row_builder(self):
        """Initialize the row builder with add/remove row functionality."""
        self.row_fields = RowFields(self.row_frame)
        self.row_fields.init_row_controls()

    def update_outputs(self):
        """Calculate and update the preview frame based on the inputs."""
        try:
            row_data = self.row_fields.get_row_data()
            update_outputs(self.preview_frame, self.input_fields, row_data)
        except ValueError as e:
            # Handle error: show a warning dialog
            self.show_warning_dialog(str(e))

    def show_warning_dialog(self, message):
        from tkinter import messagebox

        messagebox.showwarning("Invalid Input", message)


if __name__ == "__main__":
    app = App()
    app.mainloop()
