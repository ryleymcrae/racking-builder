# spacings = [12, 16, 18, 19.1875, 24, 32, 48]
# first_bracket_inset = 10
# orientation = "Landscape"
# pattern = "Staggered"
# num_panels = 11
# panel_height = round(2094 / 25.4, 4)
# panel_width = round(1134 / 25.4)
# rafter_spacing = 24
# rail_protrusion = 4
# panel_spacing = 5 / 8

# # for s in spacings:
# # print(f"{s}:\t{(48 // s) * s}")

# if orientation == "Landscape":
#     row_length = num_panels * panel_height + (num_panels - 1) * panel_spacing
# else:
#     row_length = num_panels * panel_width + (num_panels - 1) * panel_spacing

# rail_length = row_length + 2 * rail_protrusion
# mount_spacing = (48 // rafter_spacing) * rafter_spacing

# if pattern == "Continuous":
#     num_mounts = 2 * ((row_length - 2 * first_bracket_inset) // mount_spacing + 2)
# else:
#     num_mounts = (
#         (row_length - 2 * first_bracket_inset - mount_spacing / 2) // mount_spacing
#         + 3  # Top row
#         + ((row_length - 2 * first_bracket_inset) // mount_spacing + 2)  # Bottom row
#     )

# print(f"Rail Length:\t{rail_length}")
# print(f"Num Mounts:\t{num_mounts}")



def optimal_rail_selection(rail_length):
    available_rails = [140, 185]  # Available rail lengths in inches
    best_combination = None  # To store the best combination found
    least_waste = float('inf')  # Start with a large value for least waste
    best_splices = 0  # To store the number of splices for the best combination
    rail_length *= 2

    # Helper function to calculate splices
    def calculate_splices(rail_combo):
        return len(rail_combo) - 1 if len(rail_combo) > 1 else 0

    # Function to calculate the rail waste for a given pattern
    def calculate_waste(rails, length_needed):
        total_length = sum(rails)
        waste = total_length - length_needed if total_length >= length_needed else float('inf')
        return waste if waste >= 0 else float('inf')

    # Iterate over all combinations of rails for the top row
    def generate_combinations():
        # Try all possible combinations of 140 and 185 inch rails
        combinations = []
        for i in range(1, int(rail_length // min(available_rails)) + 3):  # Roughly estimate the max number of rails needed
            for j in range(i + 1):  # j is the number of 140 inch rails in the combination
                num_140 = j
                num_185 = i - j
                if num_185 >= 0:
                    combination = [140] * num_140 + [185] * num_185
                    combinations.append(combination)
        return combinations

    # Try all combinations and compute the waste for both rows
    for combo in generate_combinations():
        top_waste = calculate_waste(combo, rail_length)

        if top_waste != float('inf'):  # Check if the combination works for the top row
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
    return {
        'best_combination': best_combination,
        'least_waste': round(least_waste / 2, 2),
        'splices': best_splices
    }

# Example usage
# rail_length = 52.64567
for i in range(1, 17):
    width = 1134 * i / 25.4 + (i-1) * 0.625 + 4
    result = optimal_rail_selection(width)
    print(f"Width: {width}")
    print(f"Best combination: {result['best_combination']}")
    print(f"Least waste: {result['least_waste']} inches")
    print(f"Number of splices: {result['splices']}")
    print("------------------")
