
import csv
import random
import copy
import global_variables

def write_to_file(content, mode="w"):
    """Write content to the file. Default mode is 'w' to overwrite."""
    try:
        with open("occupancy_data.txt", mode) as file:
            file.write(content)
    except Exception as e:
        print(f"Error writing to file: {e}")

def append_new_train_data(train_number, overlapping_blocks, ticket_data, new_passengers, total_count, position):
    """Append new train data to the occupancy file."""
    content = (
        f"Train {train_number}:\n"
        f"Overlapping Blocks at position {position}m: {overlapping_blocks}\n"
        f"New passengers getting on: {new_passengers}\n"
        f"Total count: {total_count}\n"
        f"Ticket Sales History: {ticket_data}\n\n"
    )
    write_to_file(content, mode="a")  # Append mode

def update_train_data(train_number, overlapping_blocks, ticket_data, new_passengers, total_count, position):
    """Update specific train data in the occupancy file."""
    try:
        # Read all lines from the file
        with open("occupancy_data.txt", "r") as file:
            lines = file.readlines()

        # Find the start of the train's data in the file
        train_start_index = None
        for i, line in enumerate(lines):
            if line.strip().startswith(f"Train {train_number}:"):
                train_start_index = i
                break

        if train_start_index is not None:
            # Modify the lines for this train
            lines[train_start_index + 1] = f"Overlapping Blocks at position {position}m: {overlapping_blocks}\n"
            lines[train_start_index + 2] = f"New passengers getting on: {new_passengers}\n"
            lines[train_start_index + 3] = f"Total count: {total_count}\n"
            lines[train_start_index + 4] = f"Ticket Sales History: {ticket_data}\n"

            # Write the updated lines back to the file
            with open("occupancy_data.txt", "w") as file:
                file.writelines(lines)
    except Exception as e:
        print(f"Error updating train data: {e}")


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

        print(f"\nTrain position: {position}m (range: {train_start}m to {train_end}m)")
        print(f"Looking for blocks in section: {block_section}\n")

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

                print(f"Block: {block_num}, Start: {block_start}, End: {block_end}")

                # Check if the train overlaps with the block
                if not (train_end < block_start or train_start > block_end):
                    overlapping_blocks.append(block_num)

                previous_end_position = block_end  # Update previous end position

            except (ValueError, KeyError, TypeError) as e:
                continue  # Skip rows with errors

        return overlapping_blocks


    def pass_count(self, station_status):
        """Calculates the number of passengers getting on and leaving."""
        if station_status == 1:
            leaving_pass = random.randint(0, self.passengers)
            starting_pass = self.passengers

            self.passengers = max(0, self.passengers - leaving_pass)
            self.new_passengers = random.randint(0, 222)
            self.passengers = min(222, self.passengers + self.new_passengers)

        return self.passengers, self.new_passengers, leaving_pass, starting_pass

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
    passengers, new_passengers, leaving_pass, starting_pass = green_line.pass_count(1)
    ticket_array = []  # Initialize an empty list
    tickets_sold = [green_line.getTickets_sold(), str(global_variables.current_time)[11:16]]
    ticket_array.append(tickets_sold)  # Append tickets_sold to the array
    update_train_data(train_number, overlapping_blocks, ticket_array, new_passengers, passengers, position)
    print(f"{train_number}, {position}, {overlapping_blocks}, {passengers}, {ticket_array}")