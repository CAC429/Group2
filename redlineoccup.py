import csv
import random
import copy

import json
import os
from beacons import beacons, BEACON_BLOCKS

def write_to_file(content, mode="w"):
    """Write content to JSON file including elevation data"""
    try:
        data = {"trains": []}
        if mode == "a":
            try:
                with open("occupancy_data.json", "r") as file:
                    data = json.load(file)
                    # Clean existing data
                    data["trains"] = [t for t in data["trains"] 
                                    if isinstance(t, dict) and t.get("number", 0) != 0]
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        
        # Parse and validate the train data
        train_data = {}
        lines = content.split('\n')
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key == "Train":
                    train_number = int(value[:-1])
                    if train_number > 0:
                        train_data["number"] = train_number
                elif key == "Position" and "number" in train_data:
                    train_data["position"] = float(value.split()[0].replace('m', ''))
                elif key == "Occupied Blocks" and "number" in train_data:
                    train_data["blocks"] = eval(value)
                elif key == "Suggested_Speed_Authority" and "number" in train_data:
                    train_data["speed_authority"] = value
                elif key == "New passengers getting on" and "number" in train_data:
                    train_data["new_passengers"] = int(value)
                elif key == "Total count" and "number" in train_data:
                    train_data["total_passengers"] = int(value)
                elif key == "Ticket Sales History" and "number" in train_data:
                    train_data["ticket_sales_history"] = eval(value)
                elif key == "Beacon Info" and value != "None" and "number" in train_data:
                    train_data["beacon_info"] = eval(value)
                elif key == "Elevation" and "number" in train_data:
                    train_data["elevation"] = float(value.split()[0].replace('m', ''))
        
        if train_data.get("number", 0) > 0:
            existing_index = next(
                (i for i, t in enumerate(data["trains"]) 
                if isinstance(t, dict) and t.get("number") == train_data["number"]), 
                None
            )
            if existing_index is not None:
                data["trains"][existing_index] = train_data
            else:
                data["trains"].append(train_data)
        
        with open("occupancy_data.json", "w") as file:
            json.dump(data, file, indent=4)
            
    except Exception as e:
        print(f"Error writing to JSON file: {e}")

def append_new_train_data(
    train_number,
    occupied_blocks,
    ticket_data,
    new_passengers,
    total_passengers,
    delta_position,
    speed_auth,
    beacon_info,
    elevation=None
):
    """Append new train data including elevation"""
    if train_number <= 0:
        return
        
    train_data = {
        "number": int(train_number),
        "position": float(delta_position),
        "blocks": [int(b) for b in occupied_blocks],
        "speed_authority": str(speed_auth),
        "new_passengers": int(new_passengers),
        "total_passengers": int(total_passengers),
        "ticket_sales_history": list(ticket_data),
        "beacon_info": beacon_info,
        "elevation": float(elevation) if elevation is not None else None
    }
    
    try:
        data = {"trains": []}
        try:
            with open("occupancy_data.json", "r") as file:
                data = json.load(file)
                data["trains"] = [t for t in data["trains"] 
                                if isinstance(t, dict) and t.get("number", 0) > 0]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        if train_number > 0:
            data["trains"].append(train_data)
            with open("occupancy_data.json", "w") as file:
                json.dump(data, file, indent=4)
            
    except Exception as e:
        print(f"Error appending train data: {e}")

def update_train_data(
    train_number,
    occupied_blocks,
    ticket_data,
    new_passengers,
    total_passengers,
    delta_position,
    speed_auth,
    beacon_info,
    elevation=None
):
    """Update train data while preventing number=0 entries"""
    if train_number <= 0:
        return
        
    try:
        data = {"trains": []}
        try:
            with open("occupancy_data.json", "r") as file:
                data = json.load(file)
                data["trains"] = [t for t in data["trains"] 
                                if isinstance(t, dict) and t.get("number", 0) > 0]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        updated_train = {
            "number": int(train_number),
            "position": float(delta_position),
            "blocks": [int(b) for b in occupied_blocks],
            "speed_authority": str(speed_auth),
            "new_passengers": int(new_passengers),
            "total_passengers": int(total_passengers),
            "ticket_sales_history": list(ticket_data),
            "beacon_info": beacon_info,
            "elevation": float(elevation) if elevation is not None else None
        }
        
        found = False
        for i, train in enumerate(data["trains"]):
            if isinstance(train, dict) and train.get("number") == train_number:
                data["trains"][i] = updated_train
                found = True
                break
        
        if not found and train_number > 0:
            data["trains"].append(updated_train)
        
        with open("occupancy_data.json", "w") as file:
            json.dump(data, file, indent=4)
        
    except Exception as e:
        print(f"Error updating train data: {e}")

def check_beacon_blocks(blocks, position):
    """Check occupied blocks against beacon locations"""
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


class RedLineOccupancy:
    def __init__(self, data):
        """Initialize the RedLineOccupancy class by loading the CSV data."""
        self.data = data
        self.passengers = 0  # Default initial passenger count
        self.station_status = 1  # Example default station status
        self.original_data = copy.deepcopy(self.data)  # Deep copy to avoid modifying original data
        self.reverse_status = 0
        self.new_passengers = 0
        self.station_cooldown = False

    def determine_section(self, position):
        """Determines the block section based on the given position (Red Line specific)."""
        if 0 <= position <= 225:
            return 'C'
        elif 225 < position <= 375:
            return 'B'
        elif 375 < position <= 525:
            return 'A'
        elif 525 < position <= 1775:
            return 'F'
        elif 1775 < position <= 2075:
            return 'G'
        elif 2075 < position <= 2275:
            return 'H'
        elif 2275 < position <= 2325:
            return 'T'
        elif 2325 < position <= 2475:
            return 'S'
        elif 2475 < position <= 2525:
            return 'R'
        elif 2525 < position <= 2825:
            return 'H'
        elif 2825 < position <= 2875:
            return 'Q'
        elif 2875 < position <= 3025:
            return 'P'
        elif 3025 < position <= 3075:
            return 'O'
        elif 3075 < position <= 3175:
            return 'H'
        elif 3175 < position <= 3400:
            return 'I'
        elif 3400 < position <= 3693.2:
            return 'J'
        elif 3693.2 < position <= 3918.2:
            return 'K'
        elif 3918.2 < position <= 4143.2:
            return 'L'
        elif 4143.2 < position <= 4368.2:
            return 'M'
        elif 4368.2 < position <= 4593.2:
            return 'N'
        elif 4593.2 < position <= 4786.4:
            return 'J'
        elif 4786.4 < position <= 5011.4:
            return 'I'
        elif 5011.4 < position <= 6151.4:
            return 'H'
        elif 6151.4 < position <= 6451.4:
            return 'G'
        elif 6451.4 < position <= 7701.4:
            return 'F'
        elif 7701.4 < position <= 7891.4:
            return 'E'
        elif 7891.4 < position <= 8116.4:
            return 'D'
        elif 8116.4 < position:
            return None
        else:
            return None

    def find_blocks(self, position):
        """
        Find all blocks that overlap with the train's length (extending 16.1m on each end from the middle).
        Returns tuple of (block_list, elevation)
        """
        block_section = self.determine_section(position)
        if block_section is None:
            print("Position out of range.")
            return [], None

        train_start = position - 16.1
        train_end = position + 16.1

        overlapping_blocks = []
        previous_end_position = 0
        current_elevation = None

        # Debug position and section
        print(f"Position: {position}m, Section: {block_section}")

        # Define the reversal condition ranges (Red Line specific)
        in_reversal_range = (0 <= position <= 525) or (2275 < position <= 2525) or \
                        (2825 < position <= 3075) or (4593.2 < position <= 8116.4)
        
        # Debug reversal status
        print(f"Reversal Active: {in_reversal_range}")

        # If the train moves outside the reversal range, reset the dataset and status
        if not in_reversal_range:
            self.data = copy.deepcopy(self.original_data)
            self.reverse_status = 0

        # Reverse the dataset only if it's within the range and has not been reversed yet
        if in_reversal_range and self.reverse_status == 0:
            print(f"Reversing dataset for position {position}")
            if 0 < position <= 525:
                self.data = [row for row in self.original_data if row.get("Section", "").strip() in ["C", "B", "A"]]
            elif 2275 < position <= 2525:
                self.data = [row for row in self.original_data if row.get("Section", "").strip() in ["T", "S", "R"]]
            elif 2825 < position <= 3075:
                self.data = [row for row in self.original_data if row.get("Section", "").strip() in ["Q", "P", "O"]]
            elif 4593.2 < position <= 8116.4:
                self.data = [row for row in self.original_data if row.get("Section", "").strip() in ["J", "I", "H", "G", "F", "E", "D"]]
            
            self.data.reverse()
            self.reverse_status = 1  # Mark as reversed

        for row in self.data:
            try:
                # Skip if Block Number is empty or invalid
                block_num_str = row.get("Block Number", "").strip()
                if not block_num_str:
                    continue

                block_num = int(float(block_num_str))
                block_section_value = row.get("Section", "").strip()

                # Skip empty or invalid section values
                if not block_section_value or block_section_value != block_section:
                    continue

                # Get elevation from grid data
                elevation = float(row.get("ELEVATION (M)", 0))  # Default to 0 if not found
                
                # Choose correct route based on position and section
                if in_reversal_range and block_section_value in ["C", "B", "A", "T", "S", "R", "Q", "P", "O", "J", "I", "H", "G", "F", "E", "D"]:
                    block_length_str = float(row["route 2"])
                else:
                    block_length_str = float(row["route 1"])

                if not block_length_str:
                    continue

                block_length = float(block_length_str)
                block_start = previous_end_position
                block_end = 0 + block_length

                # Debug block info
                #print(f"Block {block_num}: start={block_start:.1f}, end={block_end:.1f}, length={block_length:.1f}")
                print(f"{block_length}")
                # Check if the train overlaps with the block
                if (train_end >= block_start) and (train_start <= block_end):
                    overlapping_blocks.append(block_num)
                    current_elevation = elevation
                    print(f"Train overlaps with Block {block_num}")

                previous_end_position = block_end

            except (ValueError, KeyError, TypeError) as e:
                print(f"Skipping row due to error: {e}")
                continue

        print(f"Final overlapping blocks: {overlapping_blocks}")
        return overlapping_blocks, current_elevation
    def getTickets_sold(self):
        """Return the number of new passengers who bought tickets."""
        return self.new_passengers


# Example usage:
if __name__ == "__main__":
    csv_file_path = "data4.csv"  # Red Line data file
    red_line = RedLineOccupancy(load_csv(csv_file_path))
    train_number = 1 
    position = 2125  # Example train position
    overlapping_blocks, elevation = red_line.find_blocks(position)
    passengers, new_passengers, starting_pass = pass_count(10, 1)
    ticket_array = []  # Initialize an empty list
    #tickets_sold = [red_line.getTickets_sold(), str(global_variables.current_time)[11:16]]
    #ticket_array.append(tickets_sold)  # Append tickets_sold to the array
    update_train_data(
        train_number,
        overlapping_blocks,
        ticket_array,
        new_passengers,
        passengers,
        position,
        "speed_auth",
        "beacon_info",
        elevation
    )
    print(f"{train_number}, {position}, {overlapping_blocks}, {passengers}, {ticket_array}, Elevation: {elevation}")