class TrainControllerUI:
    def __init__(self, master, controller, remote_controller):
        # ... (previous code remains the same until file definitions)
        
        # Initialize variables - CHANGED TO JSON
        self.output_file = 'TC1_outputs.json'  # Changed from .txt
        self.input_file = 'train1_outputs.json'  # Changed from .txt
        self.last_modified_time = None
        # ... (rest of init remains the same)

    def read_train_outputs(self):
        try:
            with open(self.input_file, 'r') as file:
                data = json.load(file)  # Read JSON instead of parsing text

            # Process basic values
            self.current_speed = float(data.get('Actual_Speed', 0))
            self.current_authority = float(data.get('Actual_Authority', 0))
            self.delta_position = float(data.get('Delta_Position', 0))

            # Process beacon data - now expects proper JSON structure
            self.beacon_data = data.get('Beacon', {})
            self.station_distance = float(self.beacon_data.get('station_distance', float('inf')))
            self.station_side = self.beacon_data.get('station_side')
            self.arriving_station = self.beacon_data.get('arriving_station')

            # Update beacon display
            if self.arriving_station and self.station_distance != float('inf'):
                beacon_text = f"Next Station: {self.arriving_station} ({self.station_distance:.1f}m, {self.station_side} side)"
                self.beacon_label.config(text=beacon_text)
            else:
                self.beacon_label.config(text="Next Station: -- (-- m)")

            # Station approach sequence (unchanged)
            if not self.station_approach_active:
                if 0 < self.station_distance <= 10 and self.current_speed > 0:
                    self.start_station_approach()
                elif self.station_distance > 10 and self.station_approach_active:
                    self.cancel_station_approach()

            # Process failures
            self.failure_states = {
                'Brake_Fail': bool(data.get('Brake_Fail', False)),
                'Signal_Fail': bool(data.get('Signal_Fail', False)),
                'Engine_Fail': bool(data.get('Engine_Fail', False))
            }
            
            # ... (rest of the method remains the same)

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return False
        except Exception as e:
            print(f"Error reading train outputs: {e}")
            return False

    def write_commanded_power(self, power):
        output_data = {
            "Commanded_Power": round(power, 2),
            "Current_Speed": round(self.current_speed, 2),
            "Suggested_Speed": round(self.suggested_speed, 2),
            "Current_Authority": self.current_authority,
            "Suggested_Authority": self.suggested_authority,
            "Service_Brake": self.led_states['service_brake'],
            "Emergency_Brake": self.led_states['emergency_brake'],
            "Beacon": self.beacon_data,
            "Delta_Position": self.delta_position
        }
        
        try:
            with open(self.output_file, 'w') as f:
                json.dump(output_data, f, indent=4)  # Write as formatted JSON
        except Exception as e:
            self.update_status(f"Error writing commanded power: {e}", is_error=True)

    def apply_automatic_mode(self):
        try:
            with open(self.input_file, "r") as file:
                data = json.load(file)  # Read JSON instead of text

            # Process suggested speed/authority
            speed_auth = data.get("suggested_speed_authority", "0000")
            if len(speed_auth) >= 4 and all(bit in '01' for bit in speed_auth):
                if speed_auth[0] == '0':
                    self.suggested_speed = int(speed_auth[1:], 2) * 0.0625
                else:
                    self.suggested_authority = int(speed_auth[1:], 2)

            # Process other states
            self.led_states.update({
                "service_brake": bool(data.get("service_brakes", False)),
                "emergency_brake": bool(data.get("emergency_brakes", False)),
                "left_door": bool(data.get("left_door", False)),
                "right_door": bool(data.get("right_door", False)),
                "out_light": bool(data.get("outside_lights", False)),
                "cabin_light": bool(data.get("cabin_lights", False)),
                "ac": bool(data.get("ac", False)),
                "failure": bool(data.get("failure", False))
            })

            self.update_ui()
            self.send_led_states()

        except json.JSONDecodeError:
            self.update_status("Error: Invalid JSON file", is_error=True)
        except Exception as e:
            self.update_status(f"Error reading JSON file: {str(e)}", is_error=True)