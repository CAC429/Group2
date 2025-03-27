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

def determine_section(position):
    """
    Determines the block section based on the given position.
    """
    if 0 <= position <= 800:
        return 'K'
    elif 800 < position <= 1300:
        return 'L'
    elif 1300 < position <= 1600:
        return 'M'
    elif 1600 < position <= 4300:
        return 'N'
    elif 4300 < position <= 4586.6:
        return 'O'
    elif 4586.6 < position <= 5261.1:
        return 'P'
    elif 5261.1 < position <= 5486.6:
        return "Q"
    elif 5486.6 < position <= 8186.6:
        return 'N'
    elif 8186.6 < position <= 8221.6:
        return 'R'
    elif 8221.6 < position <= 8501.6:
        return 'S'
    elif 8501.6 < position <= 8991.6:
        return 'T'
    elif 8991.6 < position <= 9753.6:
        return 'U'
    elif 9753.6 < position <= 9993.6:
        return 'V'
    elif 9993.6 < position <= 11093.6:
        return 'W'
    elif 11093.6 < position <= 11243.6:
        return 'X'
    elif 11243.6 < position <= 11517.6:
        return 'Y'
    elif 11517.6 < position <= 11552.6:
        return 'Z'
    elif 11552.6 < position <= 13152.6:
        return 'F'
    elif 13152.6 < position <= 13752.6:
        return 'E'
    elif 13752.6 < position <= 14352.6:
        return 'D'
    elif 14352.6 < position <= 14952.6:
        return 'C'
    elif 14952.6 < position <= 15252.6:
        return 'B'
    elif 15252.6 < position <= 15552.6:
        return 'A'
    elif 15552.6 < position <= 16152.6:
        return 'D'
    elif 16152.6 < position <= 16752.6:
        return 'E'
    elif 16752.6 < position <= 18352.6:
        return 'F'
    elif 18352.6 < position <= 18552.6:
        return 'G'
    elif 18552.6 < position <= 18702.6:
        return 'H'
    elif 18702.6 < position <= 19802.6:
        return 'I'
    elif 19802.6 < position <= 20052.6:
        return 'J'
    else:
        return None

def find_blocks(position, data):
    """
    Find all blocks that overlap with the train's length (extending 16.1m on each end from the middle).
    """
    block_section = determine_section(position)
    if block_section is None:
        print("Position out of range.")
        return []

    train_start = position - 16.1
    train_end = position + 16.1

    print(f"\nTrain position: {position}m (range: {train_start}m to {train_end}m)")
    print(f"Looking for blocks in section: {block_section}\n")

    overlapping_blocks = []
    previous_end_position = 0  # Initialize previous end position to 0 for the first block

    if 5486.6 < position < 8186.6:
        # Filter only section 'N' blocks and reverse the order
        data = [row for row in data if row.get("Section", "").strip() == "N"]
        data.reverse()

    if 11552.6 < position < 15552.6:
        data.reverse()

    for row in data:
        try:
            block_num = int(float(row["Block Number"]))  # Convert to integer

            # Print the actual content of Block Section for debugging
            block_section_value = row.get("Section", "").strip()
            #print(f"Block Section Value: '{block_section_value}'")  # Debugging output

            # Handle empty or invalid section values
            if not block_section_value:
                #print(f"  Skipping Block {block_num} (empty Block Section value)")
                continue  # Skip if section value is empty

            # Check if the section matches the determined section
            if block_section_value != block_section:
                #print(f"  Skipping block {block_num} (not in section {block_section})")
                continue  # Skip if block is not in the determined section

            # Try to get the block length from "route 1"
            try:
                if (8186.6 >= position > 5486.6) or (11552.6 < position <= 15552.6):
                    block_length = float(row["route 2"])  # Read from "route 1" for block length
                else:
                    block_length = float(row["route 1"])  # Read from "route 1" for block length
            except ValueError:
                #print(f"  Skipping Block {block_num} (invalid route 1 value)")
                continue  # Skip if route 1 value is not a valid float

            #print(f"Checking Block {block_num} (Section: '{block_section_value}', route 1 Length: {block_length}m)")

            # Set the current block's start position based on previous block's end position
          
            block_start = previous_end_position
            block_end = 0 + block_length

            #print(f"  Block {block_num} spans {block_start}m to {block_end}m")

            # Check if the train overlaps with the block
            if not (train_end < block_start or train_start > block_end):
                #print(f"  Train overlaps with Block {block_num}")
                overlapping_blocks.append(block_num)

            # Update the previous end position for the next block
            previous_end_position = block_end

        except (ValueError, KeyError, TypeError) as e:
            #print(f"Skipping row due to error: {e}")
            continue  # Skip rows with any other errors

    #print("\nFinal overlapping blocks:", overlapping_blocks)
    return overlapping_blocks

# Load the CSV file
csv_file_path = "C:/Users/c_cra/OneDrive/Documents/Group2/data2.csv"  # Replace with actual path to your CSV
data = load_csv(csv_file_path)

# Example usage: Find blocks for a train positioned 500m from the yard
example_position = 2000
overlapping_blocks = find_blocks(example_position, data)
print(f"\nTrain at position {example_position}m is in blocks: {overlapping_blocks}")
