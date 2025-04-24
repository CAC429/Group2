from Train_Calculation import Train_Calc
from Train_Failures import Train_Failure
from Train_Component import Train_Comp
from Reference_Object import Reference_Objects
import tkinter as tk
import random
import time
import json
from tkinter import messagebox
import os
from PIL import Image, ImageTk

class MainTrainModel:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Train Model Controller")
        self.root.withdraw() 
        self.train_models = []
        self._cleanup_train_outputs()
        
        # Status frame
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(pady=10)
        self.status_label = tk.Label(
            self.status_frame, 
            text="Monitoring train instances...",
            font=('Arial', 10)
        )
        self.status_label.pack()
        
        self.monitor_train_instances()
        self.run()

    def _cleanup_train_outputs(self):
        """Deletes only trainX_outputs.json files on startup"""
        for filename in os.listdir('.'):
            if (filename.startswith('train') 
                and filename.endswith('_outputs.json') 
                and not filename.startswith('TC')):
                try:
                    os.remove(filename)
                    print(f"Deleted old train output: {filename}")
                except Exception as e:
                    print(f"Couldn't delete {filename}: {e}")

    def create_new_train(self):
        """Create a new train UI with the next available number"""
        train_number = len(self.train_models) + 1
        try:
            train_window = tk.Toplevel(self.root)
            train_window.title(f"Train {train_number} Controls")
            
            train_model = Train_Model(
                root=train_window,
                Train_Number=train_number
            )
            self.train_models.append(train_model)
            print(f"Created new Train {train_number}")
            
            self.root.deiconify()
            
        except Exception as e:
            print(f"Error creating train {train_number}: {e}")
    
    def update_status(self, current_value):
        """Update the status display"""
        self.status_label.config(
            text=f"Trains: {len(self.train_models)} | Current Instance: {current_value}",
            fg='green'
        )

    def monitor_train_instances(self):
        """Check train_instance.json and create new trains when needed"""
        try:
            with open('train_instance.json', 'r') as f:
                data = json.load(f)
                current_value = data.get('train_instance', 0)
                
            if current_value == 1:
                # Only create a new train if this is a new activation
                if not hasattr(self, 'last_instance_value') or self.last_instance_value != 1:
                    self.create_new_train()
                    
            self.last_instance_value = current_value
            self.update_status(current_value)
            
        except Exception as e:
            print(f"Error reading train instances: {e}")
            self.status_label.config(text=f"Error: {str(e)}", fg='red')
            
        # Check every second
        self.root.after(1000, self.monitor_train_instances)

    def update_trains(self, num_trains):
        """Create or destroy trains as needed"""
        # Remove excess trains if count decreased
        while len(self.train_models) > num_trains:
            train = self.train_models.pop()
            train.root.destroy()
            print(f"Destroyed train {train.Train_Number}")
            
        # Add new trains if count increased
        if num_trains > len(self.train_models):
            try:
                self.load_trains_from_file(num_trains)
            except Exception as e:
                print(f"Error creating trains: {e}")
                
        # Update window 
        if num_trains > 0:
            self.root.deiconify()
        else:
            self.root.withdraw()

    def load_trains_from_file(self, num_trains, file_path='occupancy_data.json'):
        """Load trains from file, creating new ones as needed"""
        try:
            # First check if file exists
            if not os.path.exists(file_path):
                self.create_default_trains(num_trains)
                return
                
            if os.path.getsize(file_path) == 0:
                messagebox.showerror("Error", f"File is empty: {file_path}")
                return

            with open(file_path, 'r') as file:
                data = json.load(file)
            
            # Handle the format with trains array or single train
            trains_data = data['trains'] if 'trains' in data else [data]

            # Create only the missing trains
            for i in range(len(self.train_models) + 1, num_trains + 1):
                try:
                    train_data = next((t for t in trains_data if t.get('number') == i), None)
                    
                    # Create train window
                    train_window = tk.Toplevel(self.root)
                    train_window.title(f"Train {i} Controls")
                    
                    beacon_info = train_data.get('beacon_info', "No beacon info") if train_data else "No beacon info"
                    if beacon_info and isinstance(beacon_info, dict):
                        beacon_str = f"station_side: {beacon_info.get('station_side', 'unknown')}, "
                        beacon_str += f"arriving_station: {beacon_info.get('arriving_station', 'UNKNOWN')}, "
                        beacon_str += f"new_station: {beacon_info.get('new_station', 'UNKNOWN')}, "
                        beacon_str += f"station_distance: {beacon_info.get('station_distance', 0)}"
                        beacon_info = beacon_str
                    
                    train_model = Train_Model(
                        root=train_window,
                        Train_Number=i,
                        Passenger_Number=train_data.get('total_passengers', 0) if train_data else 0,
                        Suggested_Speed_Authority=train_data.get('speed_authority', "0") if train_data else "0",
                        Beacon=beacon_info,
                        elevation=train_data.get('elevation', 0.0) if train_data else 0.0
                    )
                    self.train_models.append(train_model)
                    print(f"Created train {i}")
                    
                except Exception as e:
                    print(f"Error creating train {i}: {e}")
                    
        except Exception as e:
            print(f"Error loading train data: {e}")

    def create_default_trains(self, num_trains):
        """Create trains with default values"""
        for i in range(len(self.train_models) + 1, num_trains + 1):
            try:
                train_window = tk.Toplevel(self.root)
                train_window.title(f"Train {i} Controls")
                
                train_model = Train_Model(
                    root=train_window,
                    Train_Number=i
                )
                self.train_models.append(train_model)
                print(f"Created default train {i}")
                
            except Exception as e:
                print(f"Error creating default train {i}: {e}")

    def run(self):
        """Main execution loop"""
        self.root.mainloop()
        

class Train_Model:
    NORMAL_ACCELERATION = 0.5 * 2.23694  # Convert 0.5 m/s² to mph/s
    def __init__(self, root, Train_Number=0, Power=0, Passenger_Number=0, Cabin_Temp=70, 
                 Right_Door=False, Left_Door=False, Exterior_Lights=True, 
                 Interior_Lights=True, Beacon="No beacon info", Suggested_Speed_Authority="0",
                 emergency_brake=0, service_brake=0, elevation=0.0):
        
        self.actual_speed_mps = 0  # Speed in meters per second
        self.cumulative_delta_meters = 0
        self.ui_activated_brake = False
        
        # Initialize all attributes
        self.emergency_brake_active = bool(emergency_brake)
        self.service_brake_active = bool(service_brake)
        self.emergency_brake = emergency_brake
        self.service_brake = service_brake
        self.tc_emergency_brake = False  # Track TC emergency brake separately
        self.ui_emergency_brake = False  # Track UI emergency brake separately
        self.station_status = 0
        self.Train_Number = Train_Number
        self.last_beacon = None
        self.Suggested_Authority = 0
        self.elevation = elevation
        self.Grade = 0
        
        # Initialize logging file
        self.log_file = f"train{Train_Number}_outputs.json"
        self.tc_outputs_file = f"TC{Train_Number}_outputs.json"
        
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
        self.Train_Ca = Train_Calc(1, 40900, 0.1, 0.1) #delta time, train weight (constant), initial Actual Speed, intial Actual Authority, elevation from occupancy_data
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

    def parse_beacon_info(self, beacon_info):
        """Parse beacon info to extract arriving and next stations"""
        arriving_station = "Unknown"
        next_station = "Unknown"
        
        if isinstance(beacon_info, dict) and not self.Train_F.Signal_Pickup_Fail:
            try:
                arriving_station = beacon_info.get("arriving_station", "Unknown")
                next_station = beacon_info.get("new_station", "Unknown")
            except Exception as e:
                print(f"Error parsing beacon info: {e}")
        elif isinstance(beacon_info, str) and not self.Train_F.Signal_Pickup_Fail:
            try:
                # Fallback to string parsing if needed
                parts = [p.strip() for p in beacon_info.split(',')]
                for part in parts:
                    if 'arriving_station:' in part:
                        arriving_station = part.split('arriving_station:')[1].strip()
                    elif 'new_station:' in part:
                        next_station = part.split('new_station:')[1].strip()
            except Exception as e:
                print(f"Error parsing beacon string: {e}")
        
        return arriving_station, next_station 

    def read_tc_outputs(self):
        """Read train-specific TC outputs file"""
        file_path = self.tc_outputs_file
        try: 
            if not os.path.exists(file_path):
                return False
                    
            with open(file_path, 'r') as file:
                data = json.load(file)
                    
            # Get the new emergency brake value from TC_outputs
            new_tc_emergency_brake = int(float(data.get('Emergency Brake', 0)))
            new_service_brake = int(float(data.get('Service Brake', 0)))
            
            # Handle TC emergency brake changes
            if new_tc_emergency_brake == 1 and not self.tc_emergency_brake:
                self.tc_emergency_brake = True
                self.activate_emergency_brake()
            elif new_tc_emergency_brake == 0 and self.tc_emergency_brake:
                self.tc_emergency_brake = False
                # Only release if UI isn't also holding the brake
                if not self.ui_emergency_brake and not self.Train_F.Engine_Fail:
                    self.release_emergency_brake()
            
            # Handle service brake changes from TC
            if new_service_brake == 1 and not self.service_brake_active:
                self.service_brake = 1
                self.activate_service_brake()
            elif new_service_brake == 0 and self.service_brake_active:
                self.service_brake = 0
                self.service_brake_active = False
                if not self.Train_F.Engine_Fail and not self.tc_emergency_brake:
                    self.update_acceleration_display()
            
            # Handle service brake changes from TC
            if new_service_brake == 1 and not self.service_brake_active:
                self.service_brake = 1
                self.activate_service_brake()
            elif new_service_brake == 0 and self.service_brake_active:
                self.service_brake = 0
                self.service_brake_active = False
                if not self.Train_F.Engine_Fail and not (self.tc_emergency_brake or self.ui_emergency_brake):
                    self.update_acceleration_display()
            
            if not self.Train_F.Engine_Fail:  # Only update power if no engine failure
                new_power = float(data.get('Commanded Power', 0))
                self.pre_failure_power = new_power  # Store in case failure occurs later
                self.Power = new_power
            
            self.Left_Door = bool(int(float(data.get('Left Door', 0))))
            self.Right_Door = bool(int(float(data.get('Right Door', 0))))
            
            # Handle new light controls
            self.Interior_Lights = bool(int(float(data.get('Cabin Lights', True))))
            self.Exterior_Lights = bool(int(float(data.get('Exterior Lights', True))))
            
            # Handle temperature control
            new_temp = float(data.get('Cabin Temp', 70))
            if 60 <= new_temp <= 85:  # Validate temperature range
                self.Cabin_Temp = new_temp
            
            # Handle suggested speed/authority - ignore if signal pickup failure
            if not self.Train_F.Signal_Pickup_Fail:
                self.Suggested_Speed = float(data.get('Suggested Speed', 0))
                self.Suggested_Authority = float(data.get('Suggested Authority', 0))
            else:
                self.Suggested_Speed = 0
                self.Suggested_Authority = 0

            return True
        except Exception as e:
            print(f"Error reading TC outputs: {e}")
            return False
        
    def release_emergency_brake(self):
        """Release the emergency brake and update physics"""
        self.emergency_brake_active = False
        if not self.service_brake_active and not self.Train_F.Engine_Fail:
            self.update_acceleration_display()
        self.write_outputs_to_file()

    def read_track_model_outputs(self, file_path='occupancy_data.json'):
        try: 
            with open(file_path, 'r') as file:
                data = json.load(file)
                    
            # Find data for this specific train
            train_data = None
            if 'trains' in data:  # New format with trains array
                for train in data['trains']:
                    if train.get('number') == self.Train_Number:
                        train_data = train
                        break
            elif data.get('number') == self.Train_Number:  # Old single-train format
                train_data = data
                    
            if train_data:
                self.Passenger_Number = train_data.get('total_passengers', 0)
                self.Suggested_Speed_Authority = str(train_data.get('speed_authority', "0"))
                self.elevation = train_data.get('elevation', 0)
                # Update beacon if no signal pickup failure
                if not self.Train_F.Signal_Pickup_Fail:
                    beacon_info = train_data.get('beacon_info', "No beacon info")
                    if beacon_info != "No beacon info":
                        self.Beacon = beacon_info
                self.last_update_time = time.time()
                return True
            return False
                
        except Exception as e:
            print(f"Error reading track model outputs: {e}")
            return False

    def initialize_log_file(self):
        """Initialize the log file with empty JSON structure"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump({}, f)  # Initialize with empty JSON object
        except Exception as e:
            print(f"Error initializing log file: {e}")

    def write_outputs_to_file(self):
        try:
            # Use cumulative_delta_meters directly now
            output_data = {
                "Passengers": int(self.Passenger_Number),
                "Station_Status": self.station_status,
                "Actual_Speed": self.Train_Ca.Actual_Speed,
                "Actual_Authority": self.Train_Ca.Actual_Authority * 0.3048,  # Convert feet to meters
                "Delta_Position": (self.cumulative_delta_meters+20),  # Already in meters the plus 20 was added to not make people upset
                "Emergency_Brake": 1 if (self.tc_emergency_brake or self.ui_emergency_brake) else 0,
                "Brake_Fail": int(self.Get_Brake_Fail_Status()),
                "Signal_Fail": int(self.Get_Signal_Pickup_Fail_Status()),
                "Engine_Fail": int(self.Get_Train_Engine_Fail_Status()),
                "Beacon": self.Beacon if isinstance(self.Beacon, str) else str(self.Beacon),
                "Suggested_Speed_Authority": str(self.Suggested_Speed_Authority),
            }
            
            with open(self.log_file, 'w') as f:
                json.dump(output_data, f, indent=4)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    @property
    def Cabin_Temp(self):
        return self._cabin_temp
    
    @Cabin_Temp.setter
    def Cabin_Temp(self, value):
        if 60 <= value <= 85:
            self._cabin_temp = value  # Set directly
            self.Train_C.Set_Cabin_Temp(self._cabin_temp)
            self.update_temp_display()
        
    def initialize_ui(self):
        self.root.title(f'Train {self.Train_Number} Model UI')
        self.create_frames()
        self.create_train_specs()
        self.create_calculation_display()
        self.create_component_display()
        self.create_station_info_display()
        self.create_failure_section()
        self.create_emergency_brake()
        self.create_advertisement()
        
        # Initialize station displays with current beacon info
        arriving_station, next_station = self.parse_beacon_info(self.Beacon)
        self.Arriving_Station_Label.config(text=f"Arriving at: {arriving_station}")
        self.Next_Station_Label.config(text=f"Next Station: {next_station}")
        self.last_beacon = self.Beacon
        
        self.update_all_displays()

    def create_advertisement(self):
        # Create a new frame for the advertisement
        self.Ad_Frame = tk.LabelFrame(self.root, text="Advertisement", padx=10, pady=10)
        self.Ad_Frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        
        # Store ad paths and current ad index
        self.ad_paths = [
            r"adfrtain3.jpg", #mcdonalds
            r"adfrtrain2.jpg" #minecraft
        ]
        self.current_ad = 0
        
        # Create label for ads 
        self.ad_label = tk.Label(self.Ad_Frame)
        self.ad_label.pack()
        
        # Sponsored content label
        self.sponsored_label = tk.Label(self.Ad_Frame, text="Sponsored Content", 
                                    font=('Arial', 7), fg='gray')
        self.sponsored_label.pack(anchor="e")
        
        # Start the ad rotation
        self.rotate_ads()

    def rotate_ads(self):
        try:
            # Load current ad
            img = Image.open(self.ad_paths[self.current_ad])
            
            # Resize Images Here
            max_width = 400
            max_height = 200
            width_ratio = max_width / float(img.size[0])
            height_ratio = max_height / float(img.size[1])
            ratio = min(width_ratio, height_ratio)
            new_size = (int(float(img.size[0]) * ratio), int(float(img.size[1]) * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            
            # Update the label
            ad_image = ImageTk.PhotoImage(img)
            self.ad_label.config(image=ad_image)
            self.ad_label.image = ad_image  # Keep reference
            
            # Switch to next ad for next rotation
            self.current_ad = (self.current_ad + 1) % len(self.ad_paths)
            
        except Exception as e:
            print(f"Error loading ad image: {e}")
            # Fallback to text if images fail
            self.ad_label.config(
                text="Ride in comfort with MetroRail! Enjoy our premium seating and climate-controlled cabins.",
                wraplength=400,
                justify=tk.LEFT
            )
        
        # Schedule next rotation in 10 seconds
        self.root.after(10000, self.rotate_ads)

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

        # New frame for station information
        self.Station_Frame = tk.LabelFrame(self.root, text="Station Information", padx=10, pady=10)
        self.Station_Frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        
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

        self.Power_Label = tk.Label(self.Calc_Frame, text="Commanded Power: N/A")
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

        # Updated Reference Objects display
        self.Reference_Status_Label = tk.Label(self.Ref_Frame, text=f"Beacon: {self.Beacon}")
        self.Reference_Status_Label.grid(row=0, column=0, columnspan=2, sticky="w")
        
        self.Speed_Authority_Label = tk.Label(self.Ref_Frame, text="Bauds: N/A")
        self.Speed_Authority_Label.grid(row=1, column=0, columnspan=2, sticky="w")
        
    def create_station_info_display(self):
        """Create a dedicated section for station information"""
        # Arriving station display
        tk.Label(self.Station_Frame, text="Current Station:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w")
        self.Arriving_Station_Label = tk.Label(self.Station_Frame, text="Unknown", font=('Arial', 10))
        self.Arriving_Station_Label.grid(row=0, column=1, sticky="w", padx=10)

        # Next station display
        tk.Label(self.Station_Frame, text="Next Station:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky="w")
        self.Next_Station_Label = tk.Label(self.Station_Frame, text="Unknown", font=('Arial', 10))
        self.Next_Station_Label.grid(row=1, column=1, sticky="w", padx=10)

        # Station side display
        tk.Label(self.Station_Frame, text="Station Side:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky="w")
        self.Station_Side_Label = tk.Label(self.Station_Frame, text="Unknown", font=('Arial', 10))
        self.Station_Side_Label.grid(row=2, column=1, sticky="w", padx=10)

        # Add visual separation
        tk.Label(self.Station_Frame, text="").grid(row=3, column=0)
        
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
        
    def create_emergency_brake(self): #emergency brake button
        self.Emergency_Brake_Button = tk.Button(
            self.root, 
            text='Press for Emergency Brake', 
            width=30, 
            height=2, 
            bg='red', 
            fg='white', 
            command=self.toggle_emergency_brake
        )
        self.Emergency_Brake_Button.grid(row=4, column=0, columnspan=3, pady=10)

    def toggle_emergency_brake(self):
        """Toggle emergency brake status in outputs only - no physics effect"""
        self.ui_emergency_brake = not self.ui_emergency_brake
        
        # Update button appearance only
        if self.ui_emergency_brake:
            self.Emergency_Brake_Button.config(text='Emergency Brake ACTIVATED', bg='dark red')
        else:
            self.Emergency_Brake_Button.config(text='Press for Emergency Brake', bg='red')
        
        # Immediately update outputs
        self.write_outputs_to_file()
        
        self.write_outputs_to_file()  # Immediate update
        
        # Update button appearance
        if self.ui_emergency_brake:
            self.Emergency_Brake_Button.config(text='Emergency Brake ACTIVATED', bg='dark red')
        else:
            self.Emergency_Brake_Button.config(text='Press for Emergency Brake', bg='red')
        
    def update_temp_display(self):
        self.Cabin_Temp_Display.config(text=f"Cabin Temperature: {self._cabin_temp:.1f} °F")

    def check_brake_status(self):
        # This method now mainly handles service brake since emergency brake is handled elsewhere
        if not self.Train_F.Brake_Fail:
            if self.service_brake == 1 and not self.service_brake_active:
                self.activate_service_brake()
            elif self.service_brake == 0 and self.service_brake_active:
                self.service_brake_active = False
                if not self.Train_F.Engine_Fail:
                    self.update_acceleration_display()
        
        self.write_outputs_to_file()

    def update_acceleration_display(self):
        """Update the acceleration display based on current state"""
        if not self.Train_F.Engine_Fail:
            if hasattr(self, 'Suggested_Speed') and self.Train_Ca.Actual_Speed < self.Suggested_Speed:
                accel = self.NORMAL_ACCELERATION
            else:
                accel = self.Train_Ca.Acceleration_Calc(self.Power, self.Passenger_Number)
            self.Acceleration_Label.config(text=f"Acceleration: {accel:.2f} mph/s")
    
    def update_all_displays(self):
        """Update all UI elements and write to log file"""
        try:
            # Read inputs first

            self.read_tc_outputs()
            self.read_track_model_outputs()

            # Update station information if beacon has changed
            if hasattr(self, 'last_beacon') and self.last_beacon != self.Beacon:
                arriving_station, next_station = self.parse_beacon_info(self.Beacon)
                self.Arriving_Station_Label.config(text=f"Arriving at: {arriving_station}")
                self.Next_Station_Label.config(text=f"Next Station: {next_station}")
                
                # Update station side if beacon info is a dictionary
                if isinstance(self.Beacon, dict):
                    station_side = self.Beacon.get("station_side", "unknown").upper()
                    self.Station_Side_Label.config(text=f"Station Side: {station_side}")
                
                self.last_beacon = self.Beacon
            elif not hasattr(self, 'last_beacon'):
                # First time initialization
                arriving_station, next_station = self.parse_beacon_info(self.Beacon)
                self.Arriving_Station_Label.config(text=f"Arriving at: {arriving_station}")
                self.Next_Station_Label.config(text=f"Next Station: {next_station}")
                
                if isinstance(self.Beacon, dict):
                    station_side = self.Beacon.get("station_side", "unknown").upper()
                    self.Station_Side_Label.config(text=f"Station Side: {station_side}")
                
                self.last_beacon = self.Beacon

            # Only calculate movement if not braking and no emergency brake
            if not self.emergency_brake_active and not self.service_brake_active:
                if not self.Train_F.Engine_Fail:
                    # If we have a suggested speed and we're below it, accelerate
                    if hasattr(self, 'Suggested_Speed') and self.Train_Ca.Actual_Speed < self.Suggested_Speed:
                        # Use normal acceleration rate
                        accel = self.NORMAL_ACCELERATION
                        # Update speed based on acceleration and time step
                        time_step = 1.0  # seconds
                        new_speed = min(self.Train_Ca.Actual_Speed + (accel * time_step), 
                                    self.Suggested_Speed)
                        self.Train_Ca.Actual_Speed = max(0, new_speed)
                    else:
                        # Calculate acceleration normally
                        accel = self.Train_Ca.Acceleration_Calc(self.Power, self.Passenger_Number)
                    
                    # Update authority
                    try:
                        if not self.Train_F.Signal_Pickup_Fail and hasattr(self, 'Suggested_Authority'):
                            # Calculate authority normally but don't exceed suggested authority
                            calculated_authority = self.Train_Ca.Actual_Authority_Calc(self.Power, self.Passenger_Number)
                            self.Train_Ca.Actual_Authority = min(calculated_authority, self.Suggested_Authority)
                        else:
                            # Calculate authority normally 
                            authority = self.Train_Ca.Actual_Authority_Calc(self.Power, self.Passenger_Number)
                            self.Train_Ca.Actual_Authority = max(0, authority)
                    except Exception as e:
                        print(f"Error calculating authority: {e}")
                        self.Train_Ca.Actual_Authority = 0
                
                # Update position

            # Update display values
            current_accel = 0
            if not (self.emergency_brake_active or self.service_brake_active) and not self.Train_F.Engine_Fail:
                if hasattr(self, 'Suggested_Speed') and self.Train_Ca.Actual_Speed < self.Suggested_Speed:
                    current_accel = self.NORMAL_ACCELERATION
                else:
                    current_accel = self.Train_Ca.Acceleration_Calc(self.Power, self.Passenger_Number)
                # If at suggested speed, show 0 acceleration
                if hasattr(self, 'Suggested_Speed') and self.Train_Ca.Actual_Speed >= self.Suggested_Speed:
                    current_accel = 0

            self.actual_speed_mps = self.Train_Ca.Actual_Speed * 0.44704  # Convert mph to m/s
            delta_meters = self.actual_speed_mps * 1  # 1 second time step
            self.cumulative_delta_meters += max(0, delta_meters)

            self.Speed_Label.config(text=f"Actual Speed: {self.Train_Ca.Actual_Speed:.2f} mph")
            self.Authority_Label.config(text=f"Actual Authority: {self.Train_Ca.Actual_Authority:.2f} ft")
            self.Acceleration_Label.config(text=f"Acceleration: {current_accel:.2f} mph/s")
            
            self.Power_Label.config(text=f"Commanded Power: {self.Power:.2f} W")
            self.Passenger_Label.config(text=f"Passengers: {int(self.Passenger_Number)}")
            
            # Calculate and display elevation and grade
            self.Elevation_Label.config(text=f"Elevation: {self.elevation:.2f} ft")
            Grade = (self.elevation/100)*100      #grade calculated by elevation divded by 100 ft * 100 for percent
            self.Grade_Label.config(text=f"Grade: {Grade:.2f}%")
            
            # Update other displays
            self.update_temp_display()
            
            right_door = "CLOSED" if self.Right_Door else "OPEN"
            left_door = "CLOSED" if self.Left_Door else "OPEN"
            self.Door_Status_Label.config(text=f"Right Door: {right_door}, Left Door: {left_door}")
            
            ext_lights = "ON" if self.Exterior_Lights else "OFF"
            int_lights = "ON" if self.Interior_Lights else "OFF"
            self.Lights_Status_Label.config(text=f"Exterior Lights: {ext_lights}, Interior Lights: {int_lights}")
            
            self.Reference_Status_Label.config(text=f"Beacon: {self.Beacon}")
            self.Speed_Authority_Label.config(text=f"Suggested Speed/Authority: {self.Suggested_Speed_Authority}")
            # Write outputs at the end of each update cycle
            self.write_outputs_to_file()
            
        except Exception as e:
            print(f"Error in update_all_displays: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_all_displays)


    def activate_service_brake(self):
        """Slows down the train at 1.2 m/s² (converted to mph/s) and maintains brake state"""
        if not self.emergency_brake_active:
            self.service_brake_active = True
            initial_speed = self.Train_Ca.Actual_Speed
            deceleration = -1.2 * 2.23694  # Convert m/s² to mph/s
            start_time = time.time()
            
            def update_braking():
                if not self.service_brake_active:  # Check if brake was released
                    return
                    
                elapsed = time.time() - start_time
                current_speed = max(0, initial_speed + deceleration * elapsed)
                
                self.Train_Ca.Actual_Speed = current_speed
                
                self.Speed_Label.config(text=f"Actual Speed: {current_speed:.2f} mph")
                self.Acceleration_Label.config(text=f"Acceleration: {deceleration:.2f} mph/s (Service Brake)")
                
                # Continuous output updates
                self.write_outputs_to_file()
                
                if current_speed > 0:
                    self.root.after(50, update_braking)
                else:
                    # When fully stopped, maintain service brake active
                    self.Train_Ca.Actual_Speed = 0  # Ensure speed is exactly 0
                    self.station_status = 1
                    self.train_stopped()
                    # Force write outputs immediately
                    self.write_outputs_to_file()
            
            update_braking()

    def activate_emergency_brake(self):
        """Handle emergency braking physics and station status (TC command only)"""
        # Handle brake release first
        if not self.tc_emergency_brake:
            if self.emergency_brake_active:
                self.emergency_brake_active = False
                # Only update acceleration if no other brakes are active
                if not self.service_brake_active and not self.Train_F.Engine_Fail:
                    self.update_acceleration_display()
            return

        # Only proceed if TC emergency brake is active
        self.emergency_brake_active = True
        initial_speed = self.Train_Ca.Actual_Speed
        deceleration = -6.1  # mph/s 
        start_time = time.time()
        
        def update_braking():
            # Check if brake was released
            if not self.tc_emergency_brake:
                self.emergency_brake_active = False
                # Only update if no other brakes are active
                if not self.service_brake_active and not self.Train_F.Engine_Fail:
                    self.update_acceleration_display()
                return
                
            elapsed = time.time() - start_time
            current_speed = max(0, initial_speed + deceleration * elapsed)
            
            # Update speed and displays
            self.Train_Ca.Actual_Speed = current_speed
            self.Speed_Label.config(text=f"Actual Speed: {current_speed:.2f} mph")
            self.Acceleration_Label.config(text=f"Acceleration: {deceleration:.2f} mph/s (Emergency Brake)")
                
            self.write_outputs_to_file()
            
            # Continue braking if still moving
            if current_speed > 0:
                self.root.after(50, update_braking)
            else:
                # Final update when fully stopped
                self.write_outputs_to_file()
        
        # Start the braking process
        update_braking()

    def simulate_engine_failure(self): #power is 0
        if not self.Train_F.Engine_Fail:
            self.pre_failure_power = self.Power  # Store current power before failure
            self.Power = 0  # Set power to 0
            self.Train_F.Engine_Fail = True
            self.check_failure_status()
            messagebox.showwarning("Engine Failure", 
                                "Engine has failed! Power set to 0.\n"
                                "Pull emergency brake or reset failures to stop.")

    def simulate_signal_failure(self): #beacon, suggested speed and authority unreadable
        if not self.Train_F.Signal_Pickup_Fail:
            self.Train_F.Signal_Pickup_Fail = True
            # Set default values for beacon and suggested speed/authority
            self.Beacon = "No beacon info (Signal Failure)"
            self.Suggested_Speed = 0
            self.Suggested_Authority = 0
            self.check_failure_status()

    def simulate_brake_failure(self): #service brake unusable
        if not self.Train_F.Brake_Fail:
            self.Train_F.Brake_Fail = True
            self.service_brake = 0  # Ensure service brake is off
            self.check_failure_status()

    def reset_failures(self):
        was_engine_failure = self.Train_F.Engine_Fail
        was_signal_failure = self.Train_F.Signal_Pickup_Fail
        was_brake_failure = self.Train_F.Brake_Fail
        
        self.Train_F.Reset()
        self.check_failure_status()
        
        if was_engine_failure:
            # Restore power to pre-failure value
            self.Power = self.pre_failure_power
            self.Train_Ca.Actual_Speed = max(0, self.Train_Ca.Actual_Speed)
        
        if was_signal_failure:
            # Trigger re-reading of beacon info
            self.last_beacon = None
            
        if was_brake_failure:
            # Service brake can now be activated again
            pass

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
        
    def Get_Actual_Speed(self):
        return self.Train_Ca.Actual_Speed
    
    def Get_Actual_Authority(self):
        return self.Train_Ca.Actual_Authority
    
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

    if hasattr(tk, '_default_root') and tk._default_root is not None:
        tk._default_root.destroy()
    
    main_model = MainTrainModel()
    main_model.run()
    #run train 
