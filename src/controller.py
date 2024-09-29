# controller.py
from customtkinter import CTkFrame

from enums import PanelType


def update_outputs(preview_frame, input_fields, row_data):
    """Update the preview based on input fields and row data."""
    panel_model = input_fields.get_input("panel_model")
    panel = PanelType.map()[panel_model]

    # Clear previous output
    for child in preview_frame.winfo_children():
        child.grid_forget()

    for id, (num_panels, orientation) in enumerate(row_data):
        row_frame = CTkFrame(preview_frame, fg_color="transparent")
        row_frame.grid(row=id, column=0, sticky="nsew")
        for i in range(num_panels):
            width, height = (
                (panel.width_inches, panel.height_inches)
                if orientation == "Portrait"
                else (panel.height_inches, panel.width_inches)
            )
            CTkFrame(
                row_frame,
                width=width,
                height=height,
                fg_color="black",
                corner_radius=0,
                border_width=1,
            ).grid(row=id, column=i, padx=0.625, pady=0.625, sticky="nsew")
