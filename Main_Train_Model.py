from Train_Calculation import Train_Calc
from Train_Failures import Train_Failure
from Train_Component import Train_Comp
from Reference_Object import Reference_Objects
import tkinter as tk
import random
from tkinter import messagebox

class Train_Model:
    def __init__(self, Power=50000, Passenger_Number=150, Cabin_Temp=72, 
                 Right_Door=False, Left_Door=False, Exterior_Lights=True, 
                 Interior_Lights=True, Beacon=0, Suggested_Speed_Authority=1000):
        # Initialize train parameters with default values
        self.Power = Power
        self.Passenger_Number = Passenger_Number
        self.Cabin_Temp = Cabin_Temp
        self.Right_Door = Right_Door
        self.Left_Door = Left_Door
        self.Exterior_Lights = Exterior_Lights
        self.Interior_Lights = Interior_Lights
        self.Beacon = Beacon  # Now set to 0 bits by default
        self.Suggested_Speed_Authority = Suggested_Speed_Authority
        
        # Initialize components
        self.Train_Ca = Train_Calc(0.001, 40900, 15, 1000, 4)  # dt, Weight, actual speed, actual authority, elevation
        self.Train_F = Train_Failure(False, False, False)  # Initialize with example failure states
        self.Train_C = Train_Comp(1)  # Initialize Train Components
        self.Reference = Reference_Objects(1)
        
        # Initialize UI
        self.initialize_ui()
        
        # State variables
        self.emergency_brake_active = False
        self.station_status = 0  # 0 = moving/not at station, 1 = stopped at station
        
    def initialize_ui(self):
        # Initialize the main window
        self.r = tk.Tk()
        self.r.title('Train Model UI')

        # Create frames for different sections
        self.create_frames()
        self.create_train_specs()
        self.create_calculation_display()
        self.create_component_display()
        self.create_failure_section()
        self.create_emergency_brake()
        
        # Update all displays with initial values
        self.update_all_displays()
        
    def create_frames(self):
        # Create frames for different sections
        self.Calc_Frame = tk.LabelFrame(self.r, text="Train Calculations", padx=10, pady=10)
        self.Calc_Frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.Comp_Frame = tk.LabelFrame(self.r, text="Train Components Simulation", padx=10, pady=10)
        self.Comp_Frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.Fail_Frame = tk.LabelFrame(self.r, text="Simulate Train Failures", padx=10, pady=10)
        self.Fail_Frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.Ref_Frame = tk.LabelFrame(self.r, text="Reference Objects", padx=10, pady=10)
        self.Ref_Frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.Spec_Frame = tk.LabelFrame(self.r, text="Train Specifications", padx=10, pady=10)
        self.Spec_Frame.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
    def create_train_specs(self):
        # Train Specs
        tk.Label(self.Spec_Frame, text="Train Mass is 90169.07 pounds (40.9 tons)").grid(row=0, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Train Length is 105.6 ft (32.2 m)").grid(row=1, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Train Width is 2.65 ft (8.69 m)").grid(row=2, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Train Height is 11.22 ft (3.42 m)").grid(row=3, column=0, sticky="w")
        tk.Label(self.Spec_Frame, text="Maximum of 222 passengers").grid(row=4, column=0, sticky="w")
        
    def create_calculation_display(self):
        # Labels to display calculation values
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
        # Labels to display component values
        self.Cabin_Temp_Display = tk.Label(self.Comp_Frame, text="Cabin Temperature: N/A")
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

        # Failure simulation buttons
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
            self.r, 
            text='Press for Emergency Brake', 
            width=30, 
            height=2, 
            bg='red', 
            fg='white', 
            command=self.activate_emergency_brake
        )
        self.Emergency_Brake_Button.grid(row=3, column=0, columnspan=3, pady=10)
        
    def update_all_displays(self):
        """Update all UI elements with current values"""
        # Update calculations
        actual_speed = self.Train_Ca.Actual_Speed_Calc(self.Power, self.Passenger_Number)
        actual_authority = self.Train_Ca.Actual_Authority_Calc(self.Power, self.Passenger_Number)
        acceleration = self.Train_Ca.Acceleration_Calc(self.Power, self.Passenger_Number)
        elevation = self.Train_Ca.Get_Elevation()
        grade = self.Train_Ca.Grade_Calc(self.Power, self.Passenger_Number)
        
        self.Speed_Label.config(text=f"Actual Speed: {actual_speed:.2f} mph")
        self.Authority_Label.config(text=f"Actual Authority: {actual_authority:.2f} ft")
        self.Acceleration_Label.config(text=f"Acceleration: {acceleration:.2f} mph^2")
        self.Elevation_Label.config(text=f"Elevation: {elevation:.2f} ft")
        self.Grade_Label.config(text=f"Grade: {grade:.2f}%")
        self.Power_Label.config(text=f"Power: {self.Power:.2f} W")
        self.Passenger_Label.config(text=f"Number of Passengers: {self.Passenger_Number} Passengers")
        
        # Update components
        self.Train_C.Set_Cabin_Temp(self.Cabin_Temp)
        self.Cabin_Temp_Display.config(text=f"Cabin Temperature: {self.Cabin_Temp:.2f} °F")
        
        ext_lights = "ON" if self.Exterior_Lights else "OFF"
        int_lights = "ON" if self.Interior_Lights else "OFF"
        self.Lights_Status_Label.config(text=f"Exterior Lights: {ext_lights}, Interior Lights: {int_lights}")
        
        right_door = "OPEN" if self.Right_Door else "CLOSED"
        left_door = "OPEN" if self.Left_Door else "CLOSED"
        self.Door_Status_Label.config(text=f"Right Door: {right_door}, Left Door: {left_door}")
        
        # Update reference objects - beacon is now 0 bits
        self.Reference_Status_Label.config(text=f"Beacon: {self.Beacon} bits\nSuggested Speed and Authority: {self.Suggested_Speed_Authority} bits")
        
    def simulate_engine_failure(self):
        self.Train_F.Engine_Fail = True
        self.check_failure_status()

    def simulate_signal_failure(self):
        self.Train_F.Signal_Pickup_Fail = True
        self.check_failure_status()

    def simulate_brake_failure(self):
        self.Train_F.Brake_Fail = True
        self.check_failure_status()

    def reset_failures(self):
        self.Train_F.Reset()
        self.check_failure_status()

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
        self.station_status = 0  # Emergency brake means not properly stopped at station
        
        # Get current speed from the calculation
        current_speed = self.Train_Ca.Actual_Speed_Calc(self.Power, self.Passenger_Number)
        
        # Constant deceleration of 2.73 m/s² converted to mph² (~6.1 mph²)
        deceleration = -6.1
        
        def update_braking():
            nonlocal current_speed
            
            # Update speed
            current_speed += deceleration * self.Train_Ca.Dt
            if current_speed < 0:
                current_speed = 0
            
            # Update UI
            self.Speed_Label.config(text=f"Actual Speed: {current_speed:.2f} mph")
            self.Acceleration_Label.config(text=f"Acceleration: {deceleration:.2f} mph^2")
            
            # Continue braking until stopped
            if current_speed > 0:
                self.r.after(50, update_braking)  # Update every 50ms
            else:
                # When fully stopped
                self.Acceleration_Label.config(text="Acceleration: 0.00 mph^2")
                self.Authority_Label.config(text="Actual Authority: 0.00 ft")
                messagebox.showinfo("Emergency Brake", "Train has come to a complete stop!")
                self.train_stopped()  # Update station status after complete stop
        
        # Start the braking process
        update_braking()

    def train_stopped(self):
        # Get current speed from calculation
        current_speed = self.Train_Ca.Actual_Speed_Calc(self.Power, self.Passenger_Number)
        
        # Check if speed is 0 and emergency brake is not active
        if current_speed == 0 and not self.emergency_brake_active:
            self.station_status = 1
            
            # Passenger handling - only when station_status becomes 1
            if self.Passenger_Number > 0:
                passengers_leaving = random.randint(0, self.Passenger_Number)
                self.Passenger_Number -= passengers_leaving
                self.Passenger_Label.config(text=f"Number of Passengers: {self.Passenger_Number} Passengers")
            
            return self.station_status
        else:
            self.station_status = 0
            return self.station_status
        

        #Get All output data for Train COntroller and Track Model
    def Get_Delta_Pos(self):
        Delta_Pos = self.Train_Ca.Delta_Position_Track_Model(self.Power, self.Passenger_Number)
        return Delta_Pos
    
    def Get_Actual_Speed(self):
        Actual_Speed = self.Train_Ca.Actual_Speed_Calc(self.Power, self.Passenger_Number)
        return Actual_Speed
    
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
        self.r.mainloop()
#comment 
# Create and run the train model
if __name__ == "__main__":
    train_model = Train_Model(
        Power=50000, 
        Passenger_Number=150, 
        Cabin_Temp=72, 
        Right_Door=False, 
        Left_Door=False, 
        Exterior_Lights=True, 
        Interior_Lights=True, 
        Beacon=0,  # Now set to 0 bits
        Suggested_Speed_Authority=1000
    )
    train_model.run()