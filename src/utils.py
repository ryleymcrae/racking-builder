import os
import sys
from enum import Enum
from typing import List, Tuple, Dict


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
                f"The value for '{fields.inputs[field_name].label._text}' is empty."
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
                f"The value for '{fields.inputs[field_name].label._text}' is outside the valid range of [{valid_range[0]}, {valid_range[1]}]."
            )

        user_inputs[field_name] = numeric_value

    return user_inputs


def get_equipment_data(row_data: List[Tuple[int, str]], rail_lengths, user_inputs) -> Dict[str, int]:
    """Calculate and return the required solar equipment quantities."""
    from enums import RackingPattern
    
    # Initialize equipment-related variables
    num_panels_total = 0
    num_mounts = 0
    num_mids = 0
    num_ends = 0
    num_splices_total = 0
    num_rails = {length: 0 for length in rail_lengths}

    # Extract user inputs
    panel_width = user_inputs["panel_width"]
    panel_height = user_inputs["panel_height"]
    panel_spacing = user_inputs["panel_spacing"]
    rail_protrusion = user_inputs["rail_protrusion"]
    maximum_rail_span = user_inputs["max._rail_span_btwn_anchors"]
    rafter_spacing = user_inputs["min._anchor_spacing_interval"]
    pattern = user_inputs["anchor_pattern"]
    bracket_inset = user_inputs["bracket_inset"]

    # Loop over row data and compute equipment quantities
    for num_panels, orientation in row_data:
        num_panels_total += num_panels
        num_ends += 4
        num_mids += 2 * (num_panels - 1)

        # Calculate row width based on panel orientation
        if orientation == "Landscape":
            row_width = num_panels * panel_height + (num_panels - 1) * panel_spacing
        else:
            row_width = num_panels * panel_width + (num_panels - 1) * panel_spacing

        rail_length = row_width + 2 * rail_protrusion
        mount_spacing = (maximum_rail_span // rafter_spacing) * rafter_spacing

        if pattern == RackingPattern.CONTINUOUS:
            num_mounts += 2 * ((row_width - 2 * bracket_inset) // mount_spacing + 2)
        else:
            num_mounts += (
                (row_width - 2 * bracket_inset - mount_spacing / 2) // mount_spacing
                + 3  # Top row
                + ((row_width - 2 * bracket_inset) // mount_spacing + 2)  # Bottom row
            )

        rail_counts, num_splices, _, _ = optimal_rail_selection(rail_length, rail_lengths)

        # Update rail counts and splices
        for rail_length, count in rail_counts.items():
            num_rails[rail_length] += count
        num_splices_total += num_splices

    # Return the calculated equipment quantities
    equipment = {
        "num_modules": num_panels_total,
        "num_rails": num_rails,
        "num_mounts": int(num_mounts),
        "num_mids": num_mids,
        "num_ends": num_ends,
        "num_splices": num_splices_total,
        "span_btwn_anchors": f'{mount_spacing:g}"',
    }
    return equipment


def get_row_data(row_data: List[Tuple[int, str]], rail_lengths, user_inputs) -> Dict[str, List[float]]:
    """Calculate the row lengths, rails, and wastes."""
    row_lengths = []
    all_rails = []
    all_wastes = []

    # Extract user inputs
    panel_width = user_inputs["panel_width"]
    panel_height = user_inputs["panel_height"]
    panel_spacing = user_inputs["panel_spacing"]
    rail_protrusion = user_inputs["rail_protrusion"]

    # Loop over row data to compute row lengths, rails, and wastes
    for num_panels, orientation in row_data:
        # Calculate row width based on panel orientation
        if orientation == "Landscape":
            row_width = num_panels * panel_height + (num_panels - 1) * panel_spacing
        else:
            row_width = num_panels * panel_width + (num_panels - 1) * panel_spacing

        rail_length = row_width + 2 * rail_protrusion
        rail_counts, _, waste, _ = optimal_rail_selection(rail_length, rail_lengths)

        # Store calculated values for each row
        row_lengths.append(round(rail_length, 2))
        all_rails.append(rail_counts)
        all_wastes.append(round(waste, 2))

    # Return the calculated row data
    row_data_results = {
        "row_lengths": row_lengths,
        "all_rails": all_rails,
        "all_wastes": all_wastes
    }
    return row_data_results


def optimal_rail_selection(required_rail_length, available_rails):
    from itertools import combinations_with_replacement

    rail_combo = []  # To store the best combination found
    min_rail_length = min(available_rails)
    remaining_length = required_rail_length

    if required_rail_length > max(available_rails):
        for rail_length in sorted(available_rails, reverse=True):
            if required_rail_length > rail_length + min_rail_length / 2:
                main_rail_length = rail_length
                break
        else:
            main_rail_length = min_rail_length
        while remaining_length >= main_rail_length + min_rail_length:
            rail_combo.append(main_rail_length)
            remaining_length -= main_rail_length
        

    best_last_rail_lengths = []
    min_waste = float("inf")

    for i in range(1, len(available_rails) + 1):
        for combo in combinations_with_replacement(available_rails, i):
            combo_length = sum(combo)
            if combo_length >= remaining_length:
                waste = combo_length - remaining_length
                if waste < min_waste:
                    min_waste = waste
                    best_last_rail_lengths = combo

    rail_combo.extend(best_last_rail_lengths)

    rail_counts = {length: rail_combo.count(length) * 2 for length in available_rails}
    num_splices = 0 if len(rail_combo) < 2 else (len(rail_combo) - 1) * 2
    total_waste = min_waste * 2

    # Return the best combination and the number of splices
    return rail_counts, num_splices, total_waste, rail_combo


def get_psf_data(row_data, user_inputs):
    psf_data = []

    panel_width = user_inputs["panel_width"]
    panel_height = user_inputs["panel_height"]
    panel_weight = user_inputs["panel_weight"]
    panel_spacing = user_inputs["panel_spacing"]
    bracket_inset = user_inputs["bracket_inset"]
    portrait_rail_inset = user_inputs["p_rail_inset"]
    landscape_rail_inset = user_inputs["l_rail_inset"]
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
