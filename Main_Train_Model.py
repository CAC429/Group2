from Train_Calculation import Train_Calc
from Train_Failures import Train_Failure
from Train_Component import Train_Comp
from Reference_Object import Reference_Objects
import tkinter as tk
import random
import time
from tkinter import messagebox

class Train_Model:
    def __init__(self, root, Train_Number=1, Power=10000, Passenger_Number=150, Cabin_Temp=73, 
                 Right_Door=False, Left_Door=False, Exterior_Lights=True, 
                 Interior_Lights=True, Beacon=0, Suggested_Speed_Authority=1010101000,
                 emergency_brake=0, service_brake=0):
        
        # Initialize all attributes
        self.emergency_brake_active = False
        self.service_brake_active = False
        self.emergency_brake = emergency_brake
        self.service_brake = service_brake
        self.station_status = 0
        self.Train_Number = Train_Number
        self.cumulative_distance = 0
        
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
        self.Train_Ca = Train_Calc(0.1, 40900, 20, 1000, 0)
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

                self.Power = float(data.get('Commanded Power', 0))
                self.emergency_brake = float(data.get('Emergency Brake', 0))
        except Exception as e:
            print(f"Error in file append: {e}")
            return False

    def initialize_log_file(self):
        with open(self.log_file, 'w') as f:
            f.write("Passengers: \n")
            f.write("Station_Status: \n")
            f.write("Actual_Speed: \n")
            f.write("Delta_Position: \n")  # Will be in meters
            f.write("Emergency_Brake: \n")
            f.write("Brake_Fail: \n")
            f.write("Signal_Fail: \n")
            f.write("Engine_Fail: \n")
            f.write("Beacon: \n")
            f.write("Suggested_Speed_Authority: \n")

    def write_outputs_to_file(self):
        try:
            # Convert delta position from feet to meters (1 foot = 0.3048 meters)
            delta_pos_meters = self.Get_Delta_Pos() * 0.3048
            
            data_entries = {
                "Passengers": str(self.Passenger_Number),
                "Station_Status": str(self.station_status),
                "Actual_Speed": str(self.Get_Actual_Speed()),
                "Actual_Authority": str(self.Get_Actual_Authority()),
                "Delta_Position": str(delta_pos_meters),  # Converted to meters
                "Emergency_Brake": str(int(self.Get_Emergency_Brake_Status())),
                "Brake_Fail": str(int(self.Get_Brake_Fail_Status())),
                "Signal_Fail": str(int(self.Get_Signal_Pickup_Fail_Status())),
                "Engine_Fail": str(int(self.Get_Train_Engine_Fail_Status())),
                "Beacon": str(self.Get_Beacon()),
                "Suggested_Speed_Authority": str(self.Get_Suggested_Speed_Authority()),
            }
            
            with open(self.log_file, 'w') as f:
                for key, value in data_entries.items():
                    f.write(f"{key}: {value}\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")

    # [Rest of the class methods remain exactly the same as in your original code]
    # Only the write_outputs_to_file() method was modified to convert feet to meters

    @property
    def Cabin_Temp(self):
        return self._cabin_temp
    
    @Cabin_Temp.setter
    def Cabin_Temp(self, value):
        if 60 <= value <= 85:
            self.target_temp = value
            self.update_temp_display()
        
    def initialize_ui(self):
        self.root.title('Train Model UI')
        self.create_frames()
        self.create_train_specs()
        self.create_calculation_display()
        self.create_component_display()
        self.create_failure_section()
        self.create_emergency_brake()
        self.update_all_displays()
        
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
        tk.Label(self.Spec_Frame, text="Train Mass is 90169.07 pounds (40.9 tons)").grid(row=0, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Train Length is 105.6 ft (32.2 m)").grid(row=1, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Train Width is 2.65 ft (8.69 m)").grid(row=2, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Train Height is 11.22 ft (3.42 m)").grid(row=3, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Maximum of 222 passengers").grid(row=4, column=0, sticky="w")
        
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

        self.Reference_Status_Label = tk.Label(self.Ref_Frame, text="Status: N/A")
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
        # Check brake status from external signals
        if self.emergency_brake == 1 and not self.emergency_brake_active:
            self.activate_emergency_brake()
        elif self.service_brake == 1 and not self.service_brake_active:
            self.activate_service_brake()
            
        # Only update speed if not in any brake mode and no engine failure
        if (not self.emergency_brake_active and 
            not self.service_brake_active and 
            not self.Train_F.Engine_Fail):
            current_speed = self.Train_Ca.Actual_Speed
            current_authority = self.Train_Ca.Actual_Authority
            
            acceleration = self.Train_Ca.Acceleration_Calc(self.Power, self.Passenger_Number)
            new_speed = current_speed + acceleration * self.Train_Ca.Dt
            new_authority = self.Train_Ca.Actual_Authority_Calc(self.Power, self.Passenger_Number)
            
            self.Train_Ca.Actual_Speed = max(0, new_speed)
            self.Train_Ca.Actual_Authority = max(0, new_authority)
        elif self.Train_F.Engine_Fail and not self.emergency_brake_active:
            self.Acceleration_Label.config(text="Acceleration: 0.00 mph/s (Engine Failed)")
        
        self.Get_Delta_Pos()
        
        self.Speed_Label.config(text=f"Actual Speed: {self.Train_Ca.Actual_Speed:.2f} mph")
        self.Authority_Label.config(text=f"Actual Authority: {self.Train_Ca.Actual_Authority:.2f} ft")
        if not self.Train_F.Engine_Fail and not self.service_brake_active:
            self.Acceleration_Label.config(text=f"Acceleration: {self.Train_Ca.Acceleration_Calc(self.Power, self.Passenger_Number):.2f} mph/s")
        
        elevation = self.Train_Ca.Get_Elevation()
        grade = self.Train_Ca.Grade_Calc(self.Power, self.Passenger_Number)
        self.Elevation_Label.config(text=f"Elevation: {elevation:.2f} ft")
        self.Grade_Label.config(text=f"Grade: {grade:.2f}%")
        self.Power_Label.config(text=f"Power: {self.Power:.2f} W")
        self.Passenger_Label.config(text=f"Number of Passengers: {self.Passenger_Number} Passengers")
        
        self.adjust_temperature()
        
        ext_lights = "ON" if self.Exterior_Lights else "OFF"
        int_lights = "ON" if self.Interior_Lights else "OFF"
        self.Lights_Status_Label.config(text=f"Exterior Lights: {ext_lights}, Interior Lights: {int_lights}")
        
        right_door = "OPEN" if self.Right_Door else "CLOSED"
        left_door = "OPEN" if self.Left_Door else "CLOSED"
        self.Door_Status_Label.config(text=f"Right Door: {right_door}, Left Door: {left_door}")
        
        self.Reference_Status_Label.config(text=f"Beacon: {self.Beacon} bits\nSuggested Speed and Authority: {self.Suggested_Speed_Authority} bits")
        
        self.write_outputs_to_file()
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
                messagebox.showinfo("Emergency Brake", f"Train stopped in {elapsed:.1f} seconds")
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
        current_speed_mph = self.Train_Ca.Actual_Speed
        current_speed_fps = current_speed_mph * 1.46667
        delta = current_speed_fps * self.Train_Ca.Dt
        self.cumulative_distance += max(0, delta)
        return self.cumulative_distance
    
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

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    train_model = Train_Model(
        root=root,
        Train_Number=1,
        Power=10000, 
        Passenger_Number=150, 
        Cabin_Temp=73, 
        Right_Door=False, 
        Left_Door=False, 
        Exterior_Lights=True, 
        Interior_Lights=True, 
        Beacon=0,
        Suggested_Speed_Authority=1010101000,
        emergency_brake=0,
        service_brake=0
    )
    train_model.run()