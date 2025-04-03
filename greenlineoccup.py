
import csv
import random
import copy
import global_variables
from beacons import beacons

BEACON_BLOCKS = {
    64: "beacon 1",
    72: "beacon 2",
    74: "beacon 3",
    87: "beacon 4",
    95: "beacon 5",
    # Beacon 6 has special condition (block 78 and position > 7500)
    104: "beacon 7",
    113: "beacon 8",
    122: "beacon 9",
    131: "beacon 10",
    140: "beacon 11",
    23: "beacon 12",
    17: "beacon 13",
    10: "beacon 14",
    3: "beacon 15",
    # Beacon 16 has special condition (block 15 and position > 15700)
    # Beacon 17 has special condition (block 21 and position > 15700)
    30: "beacon 18",
    38: "beacon 19",
    47: "beacon 20",
    56: "beacon 21"
}

# Update the write_to_file function to include beacon info
def write_to_file(content, mode="w"):
    """Write content to the file with speed authority and beacon information."""
    try:
        with open("occupancy_data.txt", mode) as file:
            file.write(content)
    except Exception as e:
        print(f"Error writing to file: {e}")

# Update append_new_train_data to include beacon info
def append_new_train_data(train_number, blocks, ticket_data, new_passengers, total_count, position, speed_authority="", beacon_info=None):
    """Append new train data with speed authority and beacon info."""
    beacon_text = f"Beacon Info: {beacon_info}\n" if beacon_info else "Beacon Info: None\n"
    content = (
        f"Train {train_number}:\n"
        f"Overlapping Blocks at position {position}m: {blocks}\n"
        f"Suggested_Speed_Authority: {speed_authority}\n"
        f"New passengers getting on: {new_passengers}\n"
        f"Total count: {total_count}\n"
        f"Ticket Sales History: {ticket_data}\n"
        f"{beacon_text}\n"
    )
    write_to_file(content, mode="a")

# Update update_train_data to include beacon info
def update_train_data(train_number, blocks, ticket_data, new_passengers, total_count, position, speed_authority="", beacon_info=None):
    """Update train data with speed authority and beacon info."""
    try:
        with open("occupancy_data.txt", "r") as file:
            lines = file.readlines()

        train_start_index = None
        for i, line in enumerate(lines):
            if line.strip().startswith(f"Train {train_number}:"):
                train_start_index = i
                break

        if train_start_index is not None:
            beacon_text = f"Beacon Info: {beacon_info}\n" if beacon_info else "Beacon Info: None\n"
            lines[train_start_index] = f"Train {train_number}:\n"
            lines[train_start_index + 1] = f"Overlapping Blocks at position {position}m: {blocks}\n"
            lines[train_start_index + 2] = f"Suggested_Speed_Authority: {speed_authority}\n"
            lines[train_start_index + 3] = f"New passengers getting on: {new_passengers}\n"
            lines[train_start_index + 4] = f"Total count: {total_count}\n"
            lines[train_start_index + 5] = f"Ticket Sales History: {ticket_data}\n"
            lines[train_start_index + 6] = beacon_text

            with open("occupancy_data.txt", "w") as file:
                file.writelines(lines)
    except Exception as e:
        print(f"Error updating train data: {e}")

# Add this new function to check for beacon blocks
def check_beacon_blocks(blocks, position):
    """Check if any of the occupied blocks is a beacon block and return the beacon info."""
    beacon_info = None
    
    for block in blocks:
        # Check special conditions first
        if block == 78 and position > 7500:
            beacon_info = beacons.get("beacon 6")
        elif block == 15 and position > 15700:
            beacon_info = beacons.get("beacon 16")
        elif block == 21 and position > 15700:
            beacon_info = beacons.get("beacon 17")
        elif block in BEACON_BLOCKS:
            beacon_info = beacons.get(BEACON_BLOCKS[block])
        
        if beacon_info:
            break
    
    return beacon_info

def pass_count(passengers, station_status):
    """Calculates the number of passengers getting on and updates count."""
    if station_status == 1:
        starting_pass = passengers  # Store initial passenger count
        total_passengers = max(0, passengers)  # Ensure non-negative passengers

        # Calculate available space on the train
        available_space = 222 - total_passengers  

        # Generate new passengers but ensure we don't exceed capacity
        new_passengers = random.randint(0, available_space)

        # Update total passengers (ensuring max is 222)
        passengers = total_passengers + new_passengers  

        print(f"New passengers: {new_passengers}, Updated total: {passengers}")
        return passengers, new_passengers, starting_pass

    return passengers, 0, passengers  # No change if not at a station


def load_csv(csv_file):
    
    """Load a CSV file into a list of dictionaries."""
    data = []
    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Error loading CSV: {e}")
    return data


class GreenLineOccupancy:
    def __init__(self, data):
        """Initialize the GreenLineOccupancy class by loading the CSV data."""
        self.data = data
        self.passengers = 0  # Default initial passenger count
        self.station_status = 1  # Example default station status
        self.original_data = copy.deepcopy(self.data)  # Deep copy to avoid modifying original data
        self.reverse_status = 0
        self.new_passengers = 0

    def determine_section(self, position):
        """Determines the block section based on the given position."""
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

    def find_blocks(self, position):
        """
        Find all blocks that overlap with the train's length (extending 16.1m on each end from the middle).
        """
        block_section = self.determine_section(position)
        if block_section is None:
            print("Position out of range.")
            return []

        train_start = position - 16.1
        train_end = position + 16.1

        #print(f"\nTrain position: {position}m (range: {train_start}m to {train_end}m)")
        #print(f"Looking for blocks in section: {block_section}\n")

        overlapping_blocks = []
        previous_end_position = 0  # Initialize previous end position to 0 for the first block

        # Define the reversal condition ranges
        in_reversal_range = (5486.6 < position <= 8186.6) or (11552.6 < position <= 15552.6)

        # If the train moves outside the reversal range, reset the dataset and status
        if not in_reversal_range:
            self.data = copy.deepcopy(self.original_data)
            self.reverse_status = 0

        # Reverse the dataset only if it's within the range and has not been reversed yet
        if in_reversal_range and self.reverse_status == 0:
            if 5486.6 < position <= 8186.6:
                self.data = [row for row in self.original_data if row.get("Section", "").strip() == "N"]
            elif 11552.6 < position <= 15552.6:
                self.data = [row for row in self.original_data if row.get("Section", "").strip() in ["F", "E", "D", "C", "B", "A"]]

            self.data.reverse()
            self.reverse_status = 1  # Mark as reversed

        for row in self.data:
            try:
                block_num = int(float(row["Block Number"]))  # Convert to integer
                block_section_value = row.get("Section", "").strip()

                # Skip empty or invalid section values
                if not block_section_value or block_section_value != block_section:
                    continue

                # Choose correct route based on position
                if in_reversal_range:
                    block_length = float(row["route 2"])
                else:
                    block_length = float(row["route 1"])

                block_start = previous_end_position
                block_end = 0 + block_length

                #print(f"Block: {block_num}, Start: {block_start}, End: {block_end}")

                # Check if the train overlaps with the block
                if not (train_end < block_start or train_start > block_end):
                    overlapping_blocks.append(block_num)

                previous_end_position = block_end  # Update previous end position

            except (ValueError, KeyError, TypeError) as e:
                continue  # Skip rows with errors

        return overlapping_blocks

    def getTickets_sold(self):
        """Return the number of new passengers who bought tickets."""
        return self.new_passengers


# Example usage:
if __name__ == "__main__":
    csv_file_path = "data2.csv"  # Replace with actual path
    green_line = GreenLineOccupancy(load_csv(csv_file_path))
    train_number = 1 
    position = 0  # Example train position
    overlapping_blocks = green_line.find_blocks(position)
    passengers, new_passengers, starting_pass = pass_count(10, 1)
    ticket_array = []  # Initialize an empty list
    tickets_sold = [green_line.getTickets_sold(), str(global_variables.current_time)[11:16]]
    ticket_array.append(tickets_sold)  # Append tickets_sold to the array
    update_train_data(train_number, overlapping_blocks, ticket_array, new_passengers, passengers, position)
    print(f"{train_number}, {position}, {overlapping_blocks}, {passengers}, {ticket_array}")