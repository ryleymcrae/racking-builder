# controller.py
from customtkinter import CTkFrame, LEFT

from enums import PanelType


def update_outputs(preview_frame, input_fields, row_data):
    """Update the preview based on input fields and row data."""
    print(row_data)
    panel_model = input_fields.get_input("panel_model")
    panel = PanelType.map()[panel_model]
    width = panel.width_inches
    height = panel.height_inches

    max_length = 0
    for _, (num_panels, orientation) in enumerate(row_data):
        if orientation == "Landscape":
            xwidth = height
        else:
            xwidth = width
        row_length = round(num_panels * xwidth) + num_panels * 2
        print(row_length)
        if row_length > 515:
            max_length = max(row_length, max_length)
            print(f"{row_length} is too long!")
    
    if max_length > 0:
        scaling_factor = 515 / max_length
        width *= scaling_factor
        height *= scaling_factor
        print(f"New width: {width}\tNew height: {height}")

    # Clear previous output
    for child in preview_frame.winfo_children():
        child.grid_forget()

    for row_num, (num_panels, orientation) in enumerate(row_data):
        row_frame = CTkFrame(preview_frame, fg_color="transparent")
        row_frame.grid(row=row_num, column=0, sticky="nsew")

        if orientation == "Landscape":
            xwidth = height  # Height becomes the width in landscape
            yheight = width   # Width becomes the height in landscape
        else:
            xwidth = width     # Normal width for portrait
            yheight = height    # Normal height for portrait

        for _ in range(num_panels):
            CTkFrame(
                row_frame,
                width=xwidth,
                height=yheight,
                fg_color="black",
                corner_radius=0,
                border_width=1,
            ).pack(side=LEFT, padx=1, pady=1,)
