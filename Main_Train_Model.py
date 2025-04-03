from Train_Calculation import Train_Calc
from Train_Failures import Train_Failure
from Train_Component import Train_Comp
from Reference_Object import Reference_Objects
import tkinter as tk
import random
import time
import ast
from tkinter import messagebox

class MainTrainModel:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        self.train_models = []
        self.load_trains_from_file()
        
    def load_trains_from_file(self, file_path='occupancy_data.txt'):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            
            train_sections = content.split('Train ')[1:]  # Skip the first empty split
        
            for section in train_sections:
                try:
                    # Extract train number (first part before colon)
                    train_number_str = section.split(':', 1)[0].strip()
                    train_number = int(train_number_str)
                    
                    # Get the rest of the section
                    train_data_str = section.split(':', 1)[1] if ':' in section else ""
                    
                    # Parse the train data
                    train_data = self.parse_train_data(train_data_str)
                    
                    # Safely get passenger count with default 0
                    passenger_count = 0
                    if 'Total count' in train_data:
                        try:
                            # First try to convert to float, then to int
                            passenger_count = int(float(train_data['Total count']))
                        except (ValueError, TypeError):
                            passenger_count = 0
                    
                    # Create a new window for each train
                    train_window = tk.Toplevel()
                    train_window.title(f"Train {train_number} Controls")
                    
                    # Create a new Train_Model instance
                    train_model = Train_Model(
                        root=train_window,
                        Train_Number=train_number,
                        Passenger_Number=passenger_count,
                        Suggested_Speed_Authority=self.process_speed_authority(
                            train_data.get('Suggested_Speed_Authority', [])),
                        Beacon=self.process_beacon_info(train_data.get('Beacon Info', None)))
                    
                    self.train_models.append(train_model)
                    
                except Exception as e:
                    print(f"Error processing train {train_number_str}: {e}")
                    continue
                    
            if not self.train_models:
                messagebox.showwarning("No Trains", "No valid train data found in the file")
                self.root.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load train data: {str(e)}")
            self.root.destroy()
            
    def parse_train_data(self, data_str):
        data = {}
        current_key = None
        current_value = []
        
        for line in data_str.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if ':' in line:
                # Store previous key-value pair if exists
                if current_key is not None:
                    data[current_key] = '\n'.join(current_value).strip()
                
                # Start new key-value pair
                key, value = line.split(':', 1)
                current_key = key.strip()
                current_value = [value.strip()]
            else:
                current_value.append(line)
                
        # Add the last key-value pair
        if current_key is not None:
            data[current_key] = '\n'.join(current_value).strip()
            
        # Convert some values from strings to Python objects
        for key in ['Suggested_Speed_Authority', 'Beacon Info']:
            if key in data and data[key] and data[key].strip().lower() not in ['none', 'null', '']:
                try:
                    # Handle list-like strings safely
                    if key == 'Suggested_Speed_Authority' and data[key].startswith('['):
                        data[key] = ast.literal_eval(data[key])
                    elif key == 'Beacon Info' and data[key].startswith('{'):
                        data[key] = ast.literal_eval(data[key])
                except (ValueError, SyntaxError):
                    pass
                    
        return data

        
    def process_speed_authority(self, speed_auth_list):
        if not speed_auth_list:
            return "0"
        # Convert list to a binary string representation
        return ''.join(str(int(x)) for x in speed_auth_list)
        
    def process_beacon_info(self, beacon_info):
        """Convert beacon info to a human-readable string"""
        # Handle None/empty cases
        if not beacon_info or str(beacon_info).strip().lower() in ['none', 'null', '']:
            return "No beacon info"
        
        # Handle dictionary format
        if isinstance(beacon_info, dict):
            parts = []
            if 'station_side' in beacon_info:
                parts.append(f"Side: {beacon_info['station_side']}")
            if 'arriving_station' in beacon_info:
                parts.append(f"Arriving: {beacon_info['arriving_station']}")
            if 'new_station' in beacon_info:
                parts.append(f"Next: {beacon_info['new_station']}")
            if 'station_distance' in beacon_info:
                try:
                    distance = float(beacon_info['station_distance'])
                    parts.append(f"Distance: {distance}m")
                except (ValueError, TypeError):
                    pass  # Skip invalid distance values
            
            return ', '.join(parts) if parts else "No valid beacon info"
        
        # Handle any other format by converting to string
        return str(beacon_info)
        
    def run(self):
        if self.train_models:  # Only run if we have trains to display
            self.root.mainloop()

class Train_Model:
    def __init__(self, root, Train_Number=1, Power=0, Passenger_Number=0, Cabin_Temp=73, 
                 Right_Door=False, Left_Door=False, Exterior_Lights=True, 
                 Interior_Lights=True, Beacon="No beacon info", Suggested_Speed_Authority="0",
                 emergency_brake=0, service_brake=0):
        
        # Initialize all attributes
        self.emergency_brake_active = False
        self.service_brake_active = False
        self.emergency_brake = emergency_brake
        self.service_brake = service_brake
        self.station_status = 0
        self.Train_Number = Train_Number
        self.cumulative_distance = 0  # Initialize to 0
        self.last_update_time = time.time()  # Track last update time
        
        # Initialize logging file
        self.log_file = f"train{Train_Number}_outputs.txt"
        
        # Initialize parameters
        self.Power = Power
        self.Passenger_Number = Passenger_Number
        self._cabin_temp = Cabin_Temp
        self.target_temp = Cabin_Temp
        self.Right_Door = Right_Door
        self.Left_Door = Left_Door
        self.Exterior_Lights = Exterior_Lights
        self.Interior_Lights = Interior_Lights
        self.Beacon = Beacon
        self.Suggested_Speed_Authority = Suggested_Speed_Authority
        
        # Initialize components
        self.Train_Ca = Train_Calc(1, 40900, 20, 1000, 0)
        self.Train_F = Train_Failure(False, False, False)
        self.Train_C = Train_Comp(1)
        self.Reference = Reference_Objects(1)
        
        self.root = root
        self.initialize_log_file()
        self.initialize_ui()

        # Activate brakes if specified
        if self.emergency_brake == 1:
            self.activate_emergency_brake()
        elif self.service_brake == 1:
            self.activate_service_brake()

    def read_tc_outputs(self, file_path='TC_outputs.txt'):
        try: 
            with open(file_path, mode='r') as file:
                lines = file.readlines()

                data = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.strip().split(':')
                        data[key.strip()] = value.strip()

                # Safely convert values with error handling
                try:
                    self.Power = float(data.get('Commanded Power', 0))
                except (ValueError, TypeError):
                    self.Power = 0
                    
                try:
                    new_emergency_brake = float(data.get('Emergency Brake', 0))
                    if new_emergency_brake == 0 and self.emergency_brake_active:
                        self.emergency_brake_active = False
                        self.emergency_brake = 0
                        if not self.service_brake_active:
                            accel = self.Train_Ca.Acceleration_Calc(self.Power, self.Passenger_Number)
                            self.Acceleration_Label.config(text=f"Acceleration: {accel:.2f} mph/s")
                except (ValueError, TypeError):
                    new_emergency_brake = 0

                self.emergency_brake = new_emergency_brake
                
                try:
                    self.service_brake = int(float(data.get('Service Brake', 0)))
                except (ValueError, TypeError):
                    self.service_brake = 0
                    
                try:
                    self.Left_Door = bool(int(float(data.get('Left Door', 0))))
                except (ValueError, TypeError):
                    self.Left_Door = False
                    
                try:
                    self.Right_Door = bool(int(float(data.get('Right Door', 0))))
                except (ValueError, TypeError):
                    self.Right_Door = False
                    
                try:
                    self.Suggested_Speed = float(data.get('Suggested Speed', 0))
                except (ValueError, TypeError):
                    self.Suggested_Speed = 0
                    
                try:
                    self.Suggested_Authority = bool(int(float(data.get('Suggested Authority', 0))))
                except (ValueError, TypeError):
                    self.Suggested_Authority = False

                return True
        except Exception as e:
            print(f"Error in file append: {e}")
            return False
        
    def read_track_model_outputs(self, file_path='occupancy_data.txt'):
        try: 
            with open(file_path, mode='r') as file:
                lines = file.readlines()

            data = {}
            for line in lines:
                if ':' in line:
                    # Split only on the first ':' to avoid unpacking errors
                    key, sep, value = line.strip().partition(':')
                    key = key.strip()
                    value = value.strip()
                    data[key] = value

                    # Extract train instance number if line starts with "Train"
                    if key.startswith('Train'):
                        train_instance = key.split('Train')[1].split(':')[0].strip()
                        try:
                            self.Train_Number = int(train_instance)
                        except ValueError:
                            print(f"Could not parse train number from: {key}")

            self.Passenger_Number = float(data.get('Total count', 0))
            self.last_update_time = time.time()  # Reset delta position timer
            return True
            
        except Exception as e:
            print(f"Error reading track model outputs: {e}")
            return False

    def initialize_log_file(self):
        """Initialize the log file by clearing any existing content"""
        try:
            # Open in write mode to clear the file
            with open(self.log_file, 'w') as f:
                # Don't write headers here - we'll write them with each update
                pass
        except Exception as e:
            print(f"Error initializing log file: {e}")

    def write_outputs_to_file(self):
        try:
            # Convert delta position from feet to meters (1 foot = 0.3048 meters)
            delta_pos_meters = self.Get_Delta_Pos() * 0.3048
            
            # Get beacon info - use the string representation we already have
            beacon_info = self.Beacon if isinstance(self.Beacon, str) else str(self.Beacon)
            
            data_entries = {
                "Passengers": str(int(self.Passenger_Number)),
                "Station_Status": str(self.station_status),
                "Actual_Speed": str(self.Get_Actual_Speed()),
                "Actual_Authority": str(self.Get_Actual_Authority()),
                "Delta_Position": str(delta_pos_meters),
                "Emergency_Brake": str(int(self.Get_Emergency_Brake_Status())),
                "Brake_Fail": str(int(self.Get_Brake_Fail_Status())),
                "Signal_Fail": str(int(self.Get_Signal_Pickup_Fail_Status())),
                "Engine_Fail": str(int(self.Get_Train_Engine_Fail_Status())),
                "Beacon": beacon_info,
                "Suggested_Speed_Authority": str(self.Get_Suggested_Speed_Authority()),
            }
            
            # Write to file in write mode to overwrite previous content
            with open(self.log_file, 'w') as f:
                for key, value in data_entries.items():
                    f.write(f"{key}: {value}\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")

    @property
    def Cabin_Temp(self):
        return self._cabin_temp
    
    @Cabin_Temp.setter
    def Cabin_Temp(self, value):
        if 60 <= value <= 85:
            self.target_temp = value
            self.update_temp_display()
        
    def initialize_ui(self):
        self.root.title(f'Train {self.Train_Number} Model UI')
        self.create_frames()
        self.create_train_specs()
        self.create_calculation_display()
        self.create_component_display()
        self.create_failure_section()
        self.create_emergency_brake()
        self.create_advertisement()
        self.update_all_displays()

    def create_advertisement(self):
        # Create a new frame for the advertisement
        self.Ad_Frame = tk.LabelFrame(self.root, text="Advertisement", padx=10, pady=10)
        self.Ad_Frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
       
        # Add advertisement text
        ad_text = "Ride in comfort with MetroRail! Enjoy our premium seating and climate-controlled cabins."
        tk.Label(self.Ad_Frame, text=ad_text, wraplength=500, justify=tk.LEFT).pack(anchor="w")
       
        tk.Label(self.Ad_Frame, text="Sponsored Content", font=('Arial', 7), fg='gray').pack(anchor="e")

    def create_frames(self):
        self.Calc_Frame = tk.LabelFrame(self.root, text="Train Calculations", padx=10, pady=10)
        self.Calc_Frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.Comp_Frame = tk.LabelFrame(self.root, text="Train Components Simulation", padx=10, pady=10)
        self.Comp_Frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.Fail_Frame = tk.LabelFrame(self.root, text="Simulate Train Failures", padx=10, pady=10)
        self.Fail_Frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.Ref_Frame = tk.LabelFrame(self.root, text="Reference Objects", padx=10, pady=10)
        self.Ref_Frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.Spec_Frame = tk.LabelFrame(self.root, text="Train Specifications", padx=10, pady=10)
        self.Spec_Frame.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
    def create_train_specs(self):
        tk.Label(self.Spec_Frame, text=f"Train {self.Train_Number} Specifications").grid(row=0, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Train Mass is 90169.07 pounds (40.9 tons)").grid(row=1, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Train Length is 105.6 ft (32.2 m)").grid(row=2, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Train Width is 2.65 ft (8.69 m)").grid(row=3, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Train Height is 11.22 ft (3.42 m)").grid(row=4, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Maximum of 222 passengers").grid(row=5, column=0, sticky="w")
        
    def create_calculation_display(self):
        self.Speed_Label = tk.Label(self.Calc_Frame, text="Actual Speed: N/A")
        self.Speed_Label.grid(row=0, column=0, columnspan=2, sticky="w")

        self.Authority_Label = tk.Label(self.Calc_Frame, text="Actual Authority: N/A")
        self.Authority_Label.grid(row=1, column=0, columnspan=2, sticky="w")

        self.Acceleration_Label = tk.Label(self.Calc_Frame, text="Acceleration: N/A")
        self.Acceleration_Label.grid(row=2, column=0, columnspan=2, sticky="w")

        self.Elevation_Label = tk.Label(self.Calc_Frame, text="Elevation: N/A")
        self.Elevation_Label.grid(row=5, column=0, columnspan=2, sticky="w")

        self.Grade_Label = tk.Label(self.Calc_Frame, text="Grade: N/A")
        self.Grade_Label.grid(row=6, column=0, columnspan=2, sticky="w")

        self.Power_Label = tk.Label(self.Calc_Frame, text="Power: N/A")
        self.Power_Label.grid(row=3, column=0, columnspan=2, sticky="w")

        self.Passenger_Label = tk.Label(self.Calc_Frame, text="Number of Passengers: N/A")
        self.Passenger_Label.grid(row=4, column=0, columnspan=2, sticky="w")
        
    def create_component_display(self):
        self.Cabin_Temp_Display = tk.Label(self.Comp_Frame, text=f"Cabin Temperature: {self._cabin_temp:.1f} °F")
        self.Cabin_Temp_Display.grid(row=0, column=0, columnspan=2, sticky="w")

        self.Lights_Status_Label = tk.Label(self.Comp_Frame, text="Exterior Lights: N/A, Interior Lights: N/A")
        self.Lights_Status_Label.grid(row=1, column=0, columnspan=2, sticky="w")

        self.Door_Status_Label = tk.Label(self.Comp_Frame, text="Right Door: N/A, Left Door: N/A")
        self.Door_Status_Label.grid(row=2, column=0, columnspan=2, sticky="w")

        self.Reference_Status_Label = tk.Label(self.Ref_Frame, text=f"Beacon: {self.Beacon}")
        self.Reference_Status_Label.grid(row=0, column=0, columnspan=2, sticky="w")
        
    def create_failure_section(self):
        self.Failure_Status_Label = tk.Label(self.Fail_Frame, text="Failure Status: All systems operational")
        self.Failure_Status_Label.grid(row=0, column=0, columnspan=2, sticky="w")

        tk.Button(self.Fail_Frame, text='Simulate Engine Failure', bg='orange', 
                 command=self.simulate_engine_failure).grid(row=1, column=0, pady=5)
        tk.Button(self.Fail_Frame, text='Simulate Signal Pickup Failure', bg='orange', 
                 command=self.simulate_signal_failure).grid(row=1, column=1, pady=5)
        tk.Button(self.Fail_Frame, text='Simulate Brake Failure', bg='orange', 
                 command=self.simulate_brake_failure).grid(row=2, column=0, pady=5)
        tk.Button(self.Fail_Frame, text='Reset Failures', bg='grey', 
                 command=self.reset_failures).grid(row=2, column=1, pady=5)
        
    def create_emergency_brake(self):
        self.Emergency_Brake_Button = tk.Button(
            self.root, 
            text='Press for Emergency Brake', 
            width=30, 
            height=2, 
            bg='red', 
            fg='white', 
            command=self.activate_emergency_brake
        )
        self.Emergency_Brake_Button.grid(row=3, column=0, columnspan=3, pady=10)
        
    def update_temp_display(self):
        self.Cabin_Temp_Display.config(text=f"Cabin Temperature: {self._cabin_temp:.1f} °F")
    
    def adjust_temperature(self):
        if abs(self._cabin_temp - self.target_temp) > 0.05:
            change = 0.1 if self.target_temp > self._cabin_temp else -0.1
            self._cabin_temp += change
            self.Train_C.Set_Cabin_Temp(self._cabin_temp)
            self.update_temp_display()
        
    def update_all_displays(self):
        """Update all UI elements and write to log file"""
        try:
            # Read from TC_outputs.txt
            self.read_tc_outputs()
            
            # Read from occupancy_data.txt - this will reset the delta position timer
            self.read_track_model_outputs()

            # Update door status displays
            right_door = "CLOSED" if self.Right_Door else "OPEN"
            left_door = "CLOSED" if self.Left_Door else "OPEN"
            self.Door_Status_Label.config(text=f"Right Door: {right_door}, Left Door: {left_door}")

            # Check brake status
            if self.emergency_brake == 1 and not self.emergency_brake_active:
                self.activate_emergency_brake()
            elif self.service_brake == 1 and not self.service_brake_active:
                self.activate_service_brake()
                
            # Update speed and authority if not in brake mode and no engine failure
            if (not self.emergency_brake_active and 
                not self.service_brake_active and 
                not self.Train_F.Engine_Fail):

                current_speed = self.Train_Ca.Actual_Speed
                
                # If suggested speed is higher than current speed, set current speed to suggested speed
                if self.Suggested_Speed > current_speed:
                    self.Train_Ca.Actual_Speed = self.Suggested_Speed
                    self.Acceleration_Label.config(text="Acceleration: 0.00 mph/s (Speed matched to suggestion)")
                
                # Update authority
                new_authority = self.Train_Ca.Actual_Authority_Calc(self.Power, self.Passenger_Number)
                self.Train_Ca.Actual_Authority = max(0, new_authority)

            elif self.Train_F.Engine_Fail and not self.emergency_brake_active:
                self.Acceleration_Label.config(text="Acceleration: 0.00 mph/s (Engine Failed)")
            
            # Update position
            self.Get_Delta_Pos()
            
            # Update speed and authority displays
            self.Speed_Label.config(text=f"Actual Speed: {self.Train_Ca.Actual_Speed:.2f} mph")
            self.Authority_Label.config(text=f"Actual Authority: {self.Train_Ca.Actual_Authority:.2f} ft")
            
            # Update other displays
            if not self.Train_F.Engine_Fail and not self.service_brake_active:
                self.Acceleration_Label.config(text=f"Acceleration: {self.Train_Ca.Acceleration_Calc(self.Power, self.Passenger_Number):.2f} mph/s")
            
            elevation = self.Train_Ca.Get_Elevation()
            grade = self.Train_Ca.Grade_Calc(self.Power, self.Passenger_Number)
            self.Elevation_Label.config(text=f"Elevation: {elevation:.2f} ft")
            self.Grade_Label.config(text=f"Grade: {grade:.2f}%")
            self.Power_Label.config(text=f"Power: {self.Power:.2f} W")
            self.Passenger_Label.config(text=f"Number of Passengers: {self.Passenger_Number} Passengers")
            
            # Update temperature
            self.adjust_temperature()
            
            # Update lights status
            ext_lights = "ON" if self.Exterior_Lights else "OFF"
            int_lights = "ON" if self.Interior_Lights else "OFF"
            self.Lights_Status_Label.config(text=f"Exterior Lights: {ext_lights}, Interior Lights: {int_lights}")
            
            # Update beacon display
            self.Reference_Status_Label.config(text=f"Beacon: {self.Beacon}")
            
            # Write to output file
            self.write_outputs_to_file()
            
        except Exception as e:
            print(f"Error in update_all_displays: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_all_displays)

    def activate_service_brake(self):
        """Slows down the train at 1.2 m/s² (converted to mph/s)"""
        if not self.emergency_brake_active:
            self.service_brake_active = True
            initial_speed = self.Train_Ca.Actual_Speed
            deceleration = -1.2 * 2.23694  # Convert m/s² to mph/s
            start_time = time.time()
            
            def update_braking():
                elapsed = time.time() - start_time
                current_speed = max(0, initial_speed + deceleration * elapsed)
                
                self.Train_Ca.Actual_Speed = current_speed
                self.Get_Delta_Pos()
                
                self.Speed_Label.config(text=f"Actual Speed: {current_speed:.2f} mph")
                self.Acceleration_Label.config(text=f"Acceleration: {deceleration:.2f} mph/s (Service Brake)")
                
                if current_speed > 0:
                    self.root.after(50, update_braking)
                else:
                    self.service_brake_active = False
                    self.station_status = 1
                    self.train_stopped()
            
            update_braking()

    def simulate_engine_failure(self):
        self.Train_F.Engine_Fail = True
        self.check_failure_status()
        messagebox.showwarning("Engine Failure", 
                             "Engine has failed! Speed is now locked.\n"
                             "Pull emergency brake or reset failures to stop.")

    def simulate_signal_failure(self):
        self.Train_F.Signal_Pickup_Fail = True
        self.check_failure_status()

    def simulate_brake_failure(self):
        self.Train_F.Brake_Fail = True
        self.check_failure_status()

    def reset_failures(self):
        was_engine_failure = self.Train_F.Engine_Fail
        self.Train_F.Reset()
        self.check_failure_status()
        if was_engine_failure:
            self.Train_Ca.Actual_Speed = max(0, self.Train_Ca.Actual_Speed)

    def check_failure_status(self):
        Status = []
        if self.Train_F.Engine_Fail:
            Status.append("Engine Failure")
        if self.Train_F.Signal_Pickup_Fail:
            Status.append("Signal Pickup Failure")
        if self.Train_F.Brake_Fail:
            Status.append("Brake Failure")

        if Status:
            self.Failure_Status_Label.config(text="Failure Status: " + ", ".join(Status))
        else:
            self.Failure_Status_Label.config(text="Failure Status: All systems operational.")

    def activate_emergency_brake(self):
        self.emergency_brake_active = True
        self.station_status = 0
        initial_speed = self.Train_Ca.Actual_Speed
        deceleration = -6.1  # mph/s
        start_time = time.time()
        
        def update_braking():
            elapsed = time.time() - start_time
            current_speed = max(0, initial_speed + deceleration * elapsed)
            
            self.Train_Ca.Actual_Speed = current_speed
            self.Get_Delta_Pos()
            
            self.Speed_Label.config(text=f"Actual Speed: {current_speed:.2f} mph")
            self.Acceleration_Label.config(text=f"Acceleration: {deceleration:.2f} mph/s")
            self.Authority_Label.config(text=f"Actual Authority: {self.Train_Ca.Actual_Authority:.2f} ft")
            
            if current_speed > 0:
                self.root.after(50, update_braking)
            else:
                self.emergency_brake_active = True
                self.Acceleration_Label.config(text="Acceleration: 0.00 mph/s")
                self.Authority_Label.config(text="Actual Authority: 0.00 ft")
                self.train_stopped()
        
        update_braking()

    def train_stopped(self):
        current_speed = self.Train_Ca.Actual_Speed
        
        if current_speed == 0 and not self.emergency_brake_active:
            self.station_status = 1
            
            if self.Passenger_Number > 0:
                passengers_leaving = random.randint(0, self.Passenger_Number)
                self.Passenger_Number -= passengers_leaving
                self.Passenger_Label.config(text=f"Number of Passengers: {self.Passenger_Number} Passengers")
            
            return self.station_status
        else:
            self.station_status = 0
            return self.station_status
        
    def Get_Delta_Pos(self):
        # Only update position if we've received new data from occupancy_data.txt
        if hasattr(self, 'last_update_time'):
            current_time = time.time()
            time_elapsed = current_time - self.last_update_time
            current_speed_mph = self.Train_Ca.Actual_Speed
            current_speed_fps = current_speed_mph * 1.46667
            delta = current_speed_fps * time_elapsed
            self.cumulative_distance += max(0, delta)
            self.last_update_time = current_time
        return self.cumulative_distance
    
    def Get_Actual_Speed(self):
        return self.Train_Ca.Actual_Speed
    
    def Get_Actual_Authority(self):
        return 10
    
    def Get_Current_Passengers(self):
        return self.Passenger_Number

    def Get_Emergency_Brake_Status(self):
        return self.emergency_brake_active

    def Get_Train_Engine_Fail_Status(self):
        return self.Train_F.Engine_Fail

    def Get_Signal_Pickup_Fail_Status(self):
        return self.Train_F.Signal_Pickup_Fail

    def Get_Brake_Fail_Status(self):
        return self.Train_F.Brake_Fail

    def Get_Beacon(self):
        return self.Beacon

    def Get_Suggested_Speed_Authority(self):
        return self.Suggested_Speed_Authority

if __name__ == "__main__":
    main_model = MainTrainModel()
    main_model.run()