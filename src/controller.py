from customtkinter import LEFT, CTkFrame, CTkLabel, CTkScrollableFrame


def update_preview_frame(preview_frame, row_data, user_inputs):
    """Update the preview based on row data."""
    max_length = 0
    panel_width, panel_height = (
        user_inputs["panel_width"],
        user_inputs["panel_height"],
    )

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


def update_results(results_frame, equipment_data, psi_data=None):
    for child in results_frame.winfo_children():
        child.destroy()

    row = 0

    hardware_label = CTkLabel(results_frame, text="Equipment")
    hardware_label.grid(row=row, columnspan=2)
    CTkFrame(results_frame, height=2).grid(
        row=row + 1, columnspan=2, padx=8, pady=(0, 4), sticky="ew"
    )
    row += 2

    for i, (key, label) in enumerate(
        {
            "num_modules": "Modules",
            "num_mounts": "Mounts",
            "num_mids": "Mids",
            "num_ends": "Ends",
            "num_splices": "Splices",
            "total_waste": "Total Waste",
        }.items()
    ):
        label = CTkLabel(results_frame, text=key.split("_")[1].capitalize())
        label.grid(row=row, column=0, padx=8, sticky="w")
        value_label = CTkLabel(results_frame, text=f"{equipment_data[key]}")
        value_label.grid(row=row, column=1, padx=8, sticky="e")
        row += 1

    for rail_length, count in equipment_data["num_rails"].items():
        label = CTkLabel(results_frame, text=f'{rail_length}" Rail')
        label.grid(row=row, column=0, padx=8, sticky="w")
        value_label = CTkLabel(results_frame, text=str(count))
        value_label.grid(row=row, column=1, padx=8, sticky="e")
        row += 1

    row_lengths_label = CTkLabel(results_frame, text="Row Lengths")
    row_lengths_label.grid(row=row, columnspan=2, pady=(16, 0))
    CTkFrame(results_frame, height=2).grid(
        row=row + 1, columnspan=2, padx=8, pady=(0, 4), sticky="ew"
    )
    row += 2

    results_frame.grid_rowconfigure(row, weight=1)
    row_lengths_frame = (
        CTkScrollableFrame(results_frame, fg_color="transparent")
        if len(equipment_data["row_lengths"]) > 5
        else CTkFrame(results_frame, fg_color="transparent")
    )
    row_lengths_frame.grid(row=row, column=0, columnspan=2, sticky="nsew")
    row_lengths_frame.grid_columnconfigure(1, weight=1)

    row_lengths = equipment_data["row_lengths"]
    all_rails = equipment_data["all_rails"]
    all_wastes = equipment_data["all_wastes"]
    for i, length in enumerate(row_lengths):
        label = CTkLabel(
            row_lengths_frame, text=f"Row {i+1}", font=("TkDefaultFont", 12, "bold")
        )
        label.grid(row=i * 2, column=0, padx=8, sticky="w")
        value_label = CTkLabel(row_lengths_frame, text=f'{length}"')
        value_label.grid(row=i * 2, column=1, padx=8, sticky="e")
        rails_label = CTkLabel(
            row_lengths_frame,
            text=f'140": {all_rails[i][0]}\t185": {all_rails[i][1]}',
            anchor="w",
            font=("TkDefaultFont", 10),
            height=20,
        )
        rails_label.grid(row=i * 2 + 1, column=0, padx=8, pady=(0, 4), sticky="w")
        waste_label = CTkLabel(
            row_lengths_frame,
            text=f'Waste: {all_wastes[i]}"',
            anchor="e",
            font=("TkDefaultFont", 10),
            height=20,
        )
        waste_label.grid(row=i * 2 + 1, column=1, padx=8, pady=(0, 4), sticky="e")
