from customtkinter import LEFT, CTkFrame


def update_preview_frame(preview_frame, row_data, panel_width, panel_height):
    """Update the preview based on row data."""
    max_length = 0

    for _, (num_panels, orientation) in enumerate(row_data):
        if orientation == "Landscape":
            xwidth = int(panel_height)
        else:
            xwidth = int(panel_width)
        row_length = round(num_panels * xwidth) + num_panels
        if row_length > 525:
            max_length = max(row_length, max_length)

    if max_length > 0:
        scaling_factor = 525 / max_length
        panel_width = int(panel_width * scaling_factor)
        panel_height = int(panel_height * scaling_factor)

    for child in preview_frame.winfo_children():
        child.grid_forget()

    for row_num, (num_panels, orientation) in enumerate(row_data):
        row_frame = CTkFrame(preview_frame, fg_color="transparent")
        row_frame.grid(row=row_num, column=0, sticky="nsew")

        if orientation == "Landscape":
            xwidth = panel_height  # Height becomes the width in landscape
            yheight = panel_width  # Width becomes the height in landscape
        else:
            xwidth = panel_width  # Normal width for portrait
            yheight = panel_height  # Normal height for portrait

        for _ in range(num_panels):
            CTkFrame(
                row_frame,
                width=xwidth,
                height=yheight,
                fg_color="black",
                corner_radius=0,
                border_width=1,
            ).pack(side=LEFT, pady=(0, 2))
