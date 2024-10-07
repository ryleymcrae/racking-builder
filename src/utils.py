import os
import sys
from enum import Enum
from typing import List, Tuple


def get_icon_path():
    """Get the path to the app's icon, depending on whether it's bundled or not."""
    if getattr(sys, "frozen", False):  # Running as an executable
        application_path = sys._MEIPASS
        return os.path.join(application_path, "icon.ico")
    else:
        return "icon.ico"


def process_fields(fields):
    """Helper method to process input fields."""
    user_inputs = {}
    for field_name in fields.inputs.keys():
        value = fields.get_input(field_name)
        
        if isinstance(value, str):
            value = value.strip()

        # Check if the input is empty
        if value == "":
            raise ValueError(
                f"The value for '{' '.join(word.capitalize() for word in field_name.split('_'))}' is empty."
            )

        # Cast the value according to its type
        variable_type = fields.get_input_variable_type(field_name)
        if issubclass(variable_type, Enum):
            numeric_value = variable_type.map()[value]  # Use enum mapping
        else:
            numeric_value = variable_type(value)

        # Check for valid range if applicable
        valid_range = fields.get_input_valid_range(field_name)
        if valid_range is not None and (
            numeric_value < valid_range[0] or numeric_value > valid_range[1]
        ):
            raise ValueError(
                f"The value for '{' '.join(word.capitalize() for word in field_name.split('_'))}' is outside the valid range of [{valid_range[0]}, {valid_range[1]}]."
            )

        user_inputs[field_name] = numeric_value

    return user_inputs


def get_equipment_data(row_data: List[Tuple[int, str]], user_inputs):
    from data_manager import DataManager
    from enums import RackingPattern

    data_manager = DataManager()

    rail_lengths = data_manager.get_rails()
    num_rails = {length: 0 for length in rail_lengths}

    num_panels_total = 0
    num_mounts = 0
    num_mids = 0
    num_ends = 0
    num_splices_total = 0
    total_waste = 0
    all_wastes = []
    all_rails = []
    row_lengths = []

    panel_width = user_inputs["panel_width"]
    panel_height = user_inputs["panel_height"]
    panel_spacing = user_inputs["panel_spacing"]
    rail_protrusion = user_inputs["rail_protrusion"]
    rafter_spacing = float(str(user_inputs["rafter_spacing"]))
    pattern = user_inputs["pattern"]
    bracket_inset = user_inputs["bracket_inset"]

    for i, (num_panels, orientation) in enumerate(row_data):
        num_panels_total += num_panels
        num_ends += 4
        num_mids += 2 * (num_panels - 1)

        if orientation == "Landscape":
            row_width = num_panels * panel_height + (num_panels - 1) * panel_spacing
        else:
            row_width = num_panels * panel_width + (num_panels - 1) * panel_spacing

        rail_length = row_width + 2 * rail_protrusion
        mount_spacing = (48 // rafter_spacing) * rafter_spacing

        if pattern == RackingPattern.CONTINUOUS:
            num_mounts += 2 * (
                (row_width - 2 * bracket_inset) // mount_spacing + 2
            )
        else:
            num_mounts += (
                (row_width - 2 * bracket_inset - mount_spacing / 2)
                // mount_spacing
                + 3  # Top row
                + (
                    (row_width - 2 * bracket_inset) // mount_spacing + 2
                )  # Bottom row
            )

        rail_counts, num_splices, waste, rails = optimal_rail_selection(
            rail_length, rail_lengths
        )

        # Update the total count of rails used
        for rail_length, count in rail_counts.items():
            num_rails[rail_length] += count

        num_splices_total += num_splices
        total_waste += waste
        all_wastes.append(round(waste, 2))
        all_rails.append(rail_counts)
        row_lengths.append(round(row_width, 2))

    equipment = {
        "num_modules": num_panels_total,
        "num_rails": num_rails,
        "num_mounts": int(num_mounts),
        "num_mids": num_mids,
        "num_ends": num_ends,
        "num_splices": num_splices_total,
        "total_waste": f'{round(total_waste, 2)}"',
        "row_lengths": row_lengths,
        "all_rails": all_rails,
        "all_wastes": all_wastes,
    }
    return equipment


def optimal_rail_selection(rail_length, available_rails):
    from itertools import combinations_with_replacement

    best_combination = None  # To store the best combination found
    least_waste = float("inf")  # Start with a large value for least waste
    best_splices = 0  # To store the number of splices for the best combination
    rail_length *= 2  # Multiply by 2 for both rows

    # Helper function to calculate splices
    def calculate_splices(rail_combo):
        n = len(rail_combo)
        if n < 3:
            return 0
        else:
            return (
                (n - 1) // 2
            ) * 2  # Add 2 splices for every two rails after the first

    # Function to calculate the rail waste for a given pattern
    def calculate_waste(rails, length_needed):
        total_length = sum(rails)
        waste = total_length - length_needed
        return waste if waste >= 0 else float("inf")

    # Generate combinations of available rails
    def generate_combinations():
        combinations = []
        for i in range(1, int(rail_length // min(available_rails)) + 3):
            for combo in combinations_with_replacement(available_rails, i):
                combinations.append(list(combo))
        return combinations

    # Try all combinations and compute the waste for both rows
    for combo in generate_combinations():
        waste = calculate_waste(combo, rail_length)

        if waste != float("inf"):
            splices = calculate_splices(combo)

            # If this configuration has less waste, update the best combination
            if waste < least_waste:
                least_waste = waste
                best_combination = combo
                best_splices = splices

    rail_counts = {length: best_combination.count(length) for length in available_rails}

    # Return the best combination and the number of splices
    return rail_counts, best_splices, least_waste, best_combination


def get_psf_data(row_data, user_inputs):
    psf_data = []

    panel_width = user_inputs["panel_width"]
    panel_height = user_inputs["panel_height"]
    panel_weight = user_inputs["panel_weight"]
    panel_spacing = user_inputs["panel_spacing"]
    bracket_inset = user_inputs["bracket_inset"]
    portrait_rail_inset = user_inputs["portrait_rail_inset"]
    landscape_rail_inset = user_inputs["landscape_rail_inset"]
    truss_structure = user_inputs["truss_structure"]

    for num_panels, orientation in row_data:
        if orientation == "Landscape":
            row_width = num_panels * panel_height + (num_panels - 1) * panel_spacing
            footprint_height = panel_width - 2 * landscape_rail_inset
        else:
            row_width = num_panels * panel_width + (num_panels - 1) * panel_spacing
            footprint_height = panel_height - 2 * portrait_rail_inset

        footprint_width = row_width - 2 * bracket_inset
        
        if truss_structure:
            footprint_area = (footprint_width + 78.7402) * (footprint_height + 78.7402)
        else:
            footprint_area = footprint_width * footprint_height

        psf = round(num_panels * panel_weight / footprint_area * 144, 2)

        psf_data.append(psf)

    return psf_data
