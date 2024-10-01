import os
import sys
from typing import List, Tuple


def get_icon_path():
    """Get the path to the app's icon, depending on whether it's bundled or not."""
    if getattr(sys, "frozen", False):  # Running as an executable
        application_path = sys._MEIPASS
        return os.path.join(application_path, "icon.ico")
    else:
        return "icon.ico"


def get_equipment_data(row_data: List[Tuple[int, str]], user_inputs):
    RAIL_LENGTHS = [140, 185]

    num_panels_total = 0
    num_rails = {length: 0 for length in RAIL_LENGTHS}
    num_mounts = 0
    num_mids = 0
    num_ends = 0
    num_splices_total = 0
    row_lengths = {}

    panel_width = user_inputs["panel_width"]
    panel_height = user_inputs["panel_height"]
    panel_spacing = user_inputs["panel_spacing"]
    rail_protrusion = user_inputs["rail_protrusion"]
    rafter_spacing = user_inputs["rafter_spacing"]
    pattern = user_inputs["pattern"]
    first_bracket_inset = user_inputs["first_bracket_inset"]

    for i, (num_panels, orientation) in enumerate(row_data):
        num_panels_total += num_panels
        num_ends += 4
        num_mids += 2 * (num_panels - 1)

        if orientation == "Landscape":
            row_length = num_panels * panel_height + (num_panels - 1) * panel_spacing
        else:
            row_length = num_panels * panel_width + (num_panels - 1) * panel_spacing

        rail_length = row_length + 2 * rail_protrusion, 4
        mount_spacing = (48 // rafter_spacing) * rafter_spacing

        if pattern == "Continuous":
            num_mounts += 2 * (
                (row_length - 2 * first_bracket_inset) // mount_spacing + 2
            )
        else:
            num_mounts += (
                (row_length - 2 * first_bracket_inset - mount_spacing / 2)
                // mount_spacing
                + 3  # Top row
                + (
                    (row_length - 2 * first_bracket_inset) // mount_spacing + 2
                )  # Bottom row
            )

        num_140, num_185, num_splices = get_rail_requirements_for_panels(
            num_panels, orientation
        )
        num_splices_total += num_splices
        num_rails[140] += num_140
        num_rails[185] += num_185
        row_lengths[i] = round(row_length, 4)

    equipment = {
        "num_modules": num_panels_total,
        "num_rails": num_rails,
        "num_mounts": int(num_mounts),
        "num_mids": num_mids,
        "num_ends": num_ends,
        "num_splices": num_splices_total,
        "row_lengths": row_lengths,
    }
    return equipment


def get_rail_requirements_for_panels(num_panels, orientation):
    portrait_lookup = {
        1: (1, 0, 0),
        2: (2, 0, 0),
        3: (0, 2, 0),
        4: (3, 0, 2),
        5: (1, 2, 2),
        6: (4, 0, 2),
        7: (2, 2, 2),
        8: (0, 4, 2),
        9: (1, 4, 4),
        10: (0, 5, 4),
        11: (2, 4, 4),
        12: (0, 6, 4),
        13: (1, 6, 6),
        14: (0, 7, 6),
        15: (2, 6, 6),
    }
    landscape_lookup = {
        1: (0, 1, 0),
        2: (0, 2, 0),
        3: (0, 3, 2),
        4: (0, 4, 2),
        5: (0, 5, 4),
        6: (2, 4, 4),
        7: (1, 6, 6),
    }
    
    # Recursive function to handle splits for panels over the maximum allowed
    def recursive_split(num_panels, orientation):
        if orientation == "Portrait":
            max_panels = 15
            lookup = portrait_lookup
        else:
            max_panels = 7
            lookup = landscape_lookup
        
        if num_panels <= max_panels:
            return lookup[num_panels]
        else:
            # Get the result for the max panels allowed
            current_result = lookup[max_panels]
            # Recursively call for the remaining panels
            remaining_result = recursive_split(num_panels - max_panels, orientation)
            
            # Sum the results index by index
            return tuple(a + b for a, b in zip(current_result, remaining_result))
    
    return recursive_split(num_panels, orientation)


def get_psi_data(row_data):
    psi_dict = {}
    return psi_dict
