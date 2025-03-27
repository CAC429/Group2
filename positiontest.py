import csv

def load_csv(csv_file):
    """
    Load a CSV file into a list of dictionaries.
    """
    data = []
    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)  # Read CSV into dictionaries
            for row in reader:
                data.append(row)  # Store rows as dictionaries
    except Exception as e:
        print(f"Error loading CSV: {e}")
    return data

def find_blocks(position, data):
    """
    Given a train position (distance from yard), find all blocks that overlap
    with the train's length (extending 16.1m on each end from the middle).

    Parameters:
    - position (float): Position of the train from the yard (meters).
    - data (list of dict): List of dictionaries containing block information.

    Returns:
    - List of valid block numbers that the train is within.
    """
    if position >= 0 and position <=800:
        block_section = 'K'

    train_start = position - 16.1
    train_end = position + 16.1

    # Initialize cumulative position tracker
    current_position = 0
    overlapping_blocks = []

    for row in data:
        try:
            block_num = int(float(row["Block Number"]))  # Convert to integer
            block_length = float(row["Block Length (m)"])  # Convert to float

            block_start = current_position
            block_end = current_position + block_length

            # Check if the train overlaps with the block
            if not (train_end < block_start or train_start > block_end):
                overlapping_blocks.append(block_num)

            # Update cumulative position
            current_position = block_end

        except (ValueError, KeyError, TypeError):
            continue  # Skip rows with missing or invalid data

    return overlapping_blocks

# Load the CSV file
csv_file_path = "C:/Users/c_cra/OneDrive/Documents/Group2/data1.csv"
data = load_csv(csv_file_path)

# Example usage: Find blocks for a train positioned 500m from the yard
example_position = 500
overlapping_blocks = find_blocks(example_position, data)
print(overlapping_blocks)