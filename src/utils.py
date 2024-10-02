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
    total_waste = 0
    all_wastes = []
    all_rails = []
    row_lengths = []

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

        rail_length = row_length + 2 * rail_protrusion
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

        num_140, num_185, num_splices, waste, rails = optimal_rail_selection(
            rail_length
        )
        num_rails[140] += num_140
        num_rails[185] += num_185
        num_splices_total += num_splices
        total_waste += waste
        all_wastes.append(round(waste, 2))
        all_rails.append((rails.count(140), rails.count(185)))
        row_lengths.append(round(row_length, 2))

    equipment = {
        "num_modules": num_panels_total,
        "num_rails": num_rails,
        "num_mounts": int(num_mounts),
        "num_mids": num_mids,
        "num_ends": num_ends,
        "num_splices": num_splices_total,
        "total_waste": f'{round(total_waste)}"',
        "row_lengths": row_lengths,
        "all_rails": all_rails,
        "all_wastes": all_wastes,
    }
    return equipment


def optimal_rail_selection(rail_length):
    available_rails = [140, 185]  # Available rail lengths in inches
    best_combination = None  # To store the best combination found
    least_waste = float("inf")  # Start with a large value for least waste
    best_splices = 0  # To store the number of splices for the best combination
    rail_length *= 2

    # Helper function to calculate splices
    def calculate_splices(rail_combo):
        n = len(rail_combo)
        if n < 3:
            return 0
        else:
            return ((n - 1) // 2) * 2

    # Function to calculate the rail waste for a given pattern
    def calculate_waste(rails, length_needed):
        total_length = sum(rails)
        waste = (
            total_length - length_needed
            if total_length >= length_needed
            else float("inf")
        )
        return waste if waste >= 0 else float("inf")

    # Iterate over all combinations of rails for the top row
    def generate_combinations():
        # Try all possible combinations of 140 and 185 inch rails
        combinations = []
        for i in range(
            1, int(rail_length // min(available_rails)) + 3
        ):  # Roughly estimate the max number of rails needed
            for j in range(
                i + 1
            ):  # j is the number of 140 inch rails in the combination
                num_140 = j
                num_185 = i - j
                if num_185 >= 0:
                    combination = [140] * num_140 + [185] * num_185
                    combinations.append(combination)
        return combinations

    # Try all combinations and compute the waste for both rows
    for combo in generate_combinations():
        top_waste = calculate_waste(combo, rail_length)

        if top_waste != float("inf"):  # Check if the combination works for the top row
            # Use the top row cutoff for the bottom row, so no additional waste
            bottom_waste = top_waste  # Since the pattern must be identical

            # Calculate the total waste and the number of splices
            total_waste = top_waste + bottom_waste
            splices = calculate_splices(combo)

            # If this configuration has less waste, update the best combination
            if total_waste < least_waste:
                least_waste = total_waste
                best_combination = combo
                best_splices = splices

    # Return the best combination and the number of splices
    return (
        best_combination.count(140),
        best_combination.count(185),
        best_splices,
        least_waste,
        best_combination,
    )


def get_psi_data(row_data):
    psi_dict = {}
    return psi_dict
