from tkinter import messagebox

from customtkinter import (
    LEFT,
    CTkButton,
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkScrollableFrame,
)


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


def update_results(results_frame, equipment_data, psf_data):
    for child in results_frame.winfo_children():
        child.destroy()

    row = 0

    hardware_label = CTkLabel(
        results_frame, text="Equipment", anchor="w", font=("TkDefaultFont", 12, "bold")
    )
    hardware_label.grid(row=row, column=0, padx=8, sticky="w")
    hardware_label = CTkLabel(
        results_frame, text="Count", anchor="e", font=("TkDefaultFont", 12, "bold")
    )
    hardware_label.grid(row=row, column=1, padx=8, sticky="e")
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

    row_lengths_label = CTkLabel(
        results_frame, text="Rows", anchor="w", font=("TkDefaultFont", 12, "bold")
    )
    row_lengths_label.grid(row=row, column=0, padx=8, pady=(16, 0), sticky="w")
    row_lengths_label = CTkLabel(
        results_frame,
        text="Deadload / Width",
        anchor="e",
        font=("TkDefaultFont", 12, "bold"),
    )
    row_lengths_label.grid(row=row, column=1, padx=8, pady=(16, 0), sticky="e")
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
        label = CTkLabel(row_lengths_frame, text=f"Row {i+1}")
        label.grid(row=i * 2, column=0, padx=8, sticky="w")
        value_label = CTkLabel(row_lengths_frame, text=f'{psf_data[i]} psf / {length}"')
        value_label.grid(row=i * 2, column=1, padx=8, sticky="e")
        rails_label = CTkLabel(
            row_lengths_frame,
            text=" ".join(
                [f'{length}": {count}' for length, count in all_rails[i].items()]
            ),
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


def edit_data(preview_frame, save_changes_callback):
    from data_manager import DataManager

    # Get the DataManager instance
    data_manager = DataManager()

    # Clear the frame
    for child in preview_frame.winfo_children():
        child.grid_forget()

    # Enable/Disable save and discard buttons
    def enable_discard():
        discard_button.configure(state="normal")

    def disable_discard():
        discard_button.configure(state="disabled")

    # Define save and discard functions
    def save_changes():
        # Convert panel widths and heights to floats
        for panel in data_manager.data["panel_models"]:
            try:
                if panel["name"] == "":
                    return messagebox.showwarning(
                        preview_frame.winfo_toplevel().title(),
                        f"Panel name cannot be empty.",
                    )
                panel["width"] = float(panel["width"])
                panel["height"] = float(panel["height"])
                panel["weight"] = float(panel["weight"])
            except ValueError:
                return messagebox.showwarning(
                    preview_frame.winfo_toplevel().title(),
                    f'Width, height, or weight for Panel "{panel["name"]}" is not valid.',
                )

        # Convert rail lengths to floats
        for i in range(len(data_manager.data["rails"])):
            try:
                data_manager.data["rails"][i] = int(data_manager.data["rails"][i])
            except ValueError:
                return messagebox.showwarning(
                    preview_frame.winfo_toplevel().title(),
                    f'Rail length "{data_manager.data["rails"][i]}" is not valid.',
                )

        # Save the data and update the UI
        data_manager.save_data()
        disable_discard()
        render_data()
        save_changes_callback()

    def discard_changes():
        # Reload the old data and update the UI
        data_manager.data = data_manager.load_data()
        disable_discard()
        render_data()

    def add_panel():
        """Add a new empty panel model."""
        data_manager.add_panel_model()
        enable_discard()
        render_data()

    def delete_panel(index):
        """Delete the panel at the given index, but warn if only 1 panel is left."""
        if len(data_manager.data["panel_models"]) == 1:
            messagebox.showwarning(
                preview_frame.winfo_toplevel().title(),
                "There must be at least one panel in the list.",
            )
        else:
            data_manager.delete_panel_model(index)
            enable_discard()
            render_data()

    def modify_panel(index, key, value):
        """Modify a specific panel's attribute."""
        data_manager.update_panel_model(index, key, value)
        enable_discard()

    def add_rail():
        """Add a new rail length."""
        data_manager.add_rail()
        enable_discard()
        render_data()

    def delete_rail(index):
        """Delete the rail at the given index, but warn if only 1 rail is left."""
        if len(data_manager.data["rails"]) == 1:
            messagebox.showwarning(
                preview_frame.winfo_toplevel().title(),
                "There must be at least one rail in the list.",
            )
        else:
            data_manager.delete_rail(index)
            enable_discard()
            render_data()

    def modify_rail(index, value):
        """Modify a specific rail length."""
        data_manager.update_rail(index, value)
        enable_discard()

    # Render the data into the frames
    def render_data():
        # Freeze UI updates
        preview_frame.update_idletasks()

        # Clear previous content in the frames
        for child in panel_frame.winfo_children():
            child.grid_forget()
        # Clear previous content in the frames
        for child in rail_frame.winfo_children():
            child.grid_forget()

        # Add column headers and "Add Panel" button in the panel_frame
        CTkLabel(
            panel_frame, text="Model Name", font=("TkDefaultFont", 13, "bold")
        ).grid(row=0, column=0, padx=8, pady=4, sticky="w")
        CTkLabel(
            panel_frame, text="Width (in.)", font=("TkDefaultFont", 13, "bold")
        ).grid(row=0, column=1, padx=8, pady=4, sticky="w")
        CTkLabel(
            panel_frame, text="Height (in.)", font=("TkDefaultFont", 13, "bold")
        ).grid(row=0, column=2, padx=8, pady=4, sticky="w")
        CTkLabel(
            panel_frame, text="Weight (lbs)", font=("TkDefaultFont", 13, "bold")
        ).grid(row=0, column=3, padx=8, pady=4, sticky="w")
        CTkButton(panel_frame, text="Add Panel", command=add_panel).grid(
            row=len(data_manager.data["panel_models"]) + 1,
            column=0,
            padx=4,
            pady=(4, 8),
        )
        # Populate panel data with editable fields
        for i, panel in enumerate(data_manager.data["panel_models"]):
            name_entry = CTkEntry(panel_frame)
            name_entry.insert(0, panel.get("name", ""))
            name_entry.grid(row=i + 1, column=0, padx=(8, 4), pady=4)
            name_entry.bind(
                "<KeyRelease>",
                lambda _, idx=i, entry=name_entry: modify_panel(
                    idx, "name", entry.get()
                ),
            )
            width_entry = CTkEntry(panel_frame, width=100)
            width_entry.insert(0, panel.get("width", ""))
            width_entry.grid(row=i + 1, column=1, padx=4, pady=4)
            width_entry.bind(
                "<KeyRelease>",
                lambda _, idx=i, entry=width_entry: modify_panel(
                    idx, "width", entry.get()
                ),
            )
            height_entry = CTkEntry(panel_frame, width=100)
            height_entry.insert(0, panel.get("height", ""))
            height_entry.grid(row=i + 1, column=2, padx=(8, 4), pady=4)
            height_entry.bind(
                "<KeyRelease>",
                lambda _, idx=i, entry=height_entry: modify_panel(
                    idx, "height", entry.get()
                ),
            )
            weight_entry = CTkEntry(panel_frame, width=100)
            weight_entry.insert(0, panel.get("weight", ""))
            weight_entry.grid(row=i + 1, column=3, padx=4, pady=4)
            weight_entry.bind(
                "<KeyRelease>",
                lambda _, idx=i, entry=weight_entry: modify_panel(
                    idx, "weight", entry.get()
                ),
            )
            CTkButton(
                panel_frame,
                text="Delete",
                width=0,
                command=lambda idx=i: delete_panel(idx),
            ).grid(row=i + 1, column=4, padx=(4, 8), pady=4)

        # Add column header and "Add Rail" button in the rail_frame
        CTkLabel(
            rail_frame, text="Length (in.)", font=("TkDefaultFont", 13, "bold")
        ).grid(row=0, column=0, padx=8, pady=4, sticky="w")

        CTkButton(rail_frame, text="Add Rail", command=add_rail).grid(
            row=len(data_manager.data["rails"]) + 1, column=0, padx=4, pady=(4, 8)
        )

        # Populate rail data with editable fields
        for i, rail in enumerate(data_manager.data["rails"]):
            rail_entry = CTkEntry(rail_frame)
            rail_entry.insert(0, rail)
            rail_entry.grid(row=i + 1, column=0, padx=(8, 4), pady=4)
            rail_entry.bind(
                "<KeyRelease>",
                lambda _, idx=i, entry=rail_entry: modify_rail(idx, entry.get()),
            )
            CTkButton(
                rail_frame,
                text="Delete",
                width=0,
                command=lambda idx=i: delete_rail(idx),
            ).grid(row=i + 1, column=1, padx=(4, 8), pady=4)

        # Apply UI updates
        preview_frame.update_idletasks()

    # Panel Models Section
    CTkLabel(
        preview_frame,
        text="Panels",
        font=("TkDefaultFont", 20, "bold"),
    ).grid(row=0, column=0, padx=4, pady=(8, 0), sticky="w")

    panel_frame = CTkFrame(preview_frame, fg_color="transparent")
    panel_frame.grid(row=1, column=0, padx=4, pady=8, sticky="w")

    # Rail Lengths Section
    CTkLabel(
        preview_frame,
        text="Rails",
        font=("TkDefaultFont", 20, "bold"),
    ).grid(row=2, column=0, padx=4, pady=(8, 0), sticky="w")

    rail_frame = CTkFrame(preview_frame, fg_color="transparent")
    rail_frame.grid(row=3, column=0, padx=4, pady=8, sticky="w")

    empty_frame = CTkFrame(preview_frame, height=50, fg_color="transparent")
    empty_frame.grid(row=4, sticky="ew")

    button_frame = CTkFrame(preview_frame.master)
    button_frame.place(x=110, y=622)

    # Save and Discard Buttons
    discard_button = CTkButton(
        button_frame, text="Discard Changes", command=discard_changes, state="disabled"
    )
    discard_button.grid(row=0, column=0, padx=(8, 0), pady=8, sticky="w")

    save_button = CTkButton(button_frame, text="Save & Close", command=save_changes)
    save_button.grid(row=0, column=1, padx=(40, 8), pady=8, sticky="w")

    # Initially render the data
    render_data()
