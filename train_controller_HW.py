import tkinter as tk
from tkinter import messagebox
from gpiozero import LED
import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import ast
import json

class PowerControl:
    def __init__(self, P_max=120, T=0.1):
        self.Kp = 0.5
        self.Ki = 0.1
        self.P_max = P_max
        self.T = T
        self.u_k_1 = 0
        self.e_k_1 = 0
        self.P_k_1 = 0
        self.direct_power_mode = False

    def update_gains(self, Kp, Ki):
        self.Kp = Kp
        self.Ki = Ki
        self.u_k_1 = 0
        self.e_k_1 = 0
        self.P_k_1 = 0

    def set_direct_power_mode(self, enable):
        self.direct_power_mode = enable
        if enable:
            self.u_k_1 = 0
            self.e_k_1 = 0

    def compute_Pcmd(self, suggested_speed, current_speed_mps, service_brake=False, emergency_brake=False, mass=50000):
        if emergency_brake:
            self.u_k_1 = 0
            self.e_k_1 = 0
            return 0

        if service_brake:
            deceleration = 1.2
            braking_force = mass * deceleration
            power_reduction = braking_force / 1000
            reduction_step = max(0, self.P_k_1 - (power_reduction * 0.35))
            P_cmd = max(0, reduction_step)
            self.u_k_1 = 0
            self.e_k_1 = 0
            self.P_k_1 = P_cmd
            return P_cmd

        if self.direct_power_mode:
            P_cmd = min(suggested_speed, self.P_max)
            self.u_k_1 = 0
            self.e_k_1 = 0
        else:
            error = suggested_speed - current_speed_mps
            u_k = self.u_k_1 + (self.T/2) * (error + self.e_k_1)
            P_cmd = self.Kp * error + self.Ki * u_k

            if P_cmd >= self.P_max:
                P_cmd = self.P_max
                u_k = self.u_k_1
            elif P_cmd <= 0:
                P_cmd = 0
                u_k = self.u_k_1

            self.u_k_1 = u_k
            self.e_k_1 = error

        self.P_k_1 = P_cmd
        return P_cmd

    def auto_tune_gains(self, target_velocity, current_velocity):
        error = target_velocity - current_velocity

        if current_velocity == 0 and target_velocity > 0:
            self.Kp = 1.5
            self.Ki = 0.2
        else:
            error_percent = abs(error) / self.P_max

            if error_percent < 0.1:
                self.Kp = 0.8
                self.Ki = 0.05
            elif error_percent < 0.3:
                self.Kp = 1.2
                self.Ki = 0.1
            else:
                self.Kp = 2.0
                self.Ki = 0.2

        return self.Kp, self.Ki

class train_controller_ui(tk.Tk):
    def __init__(self, controller, oled, text_file):
        super().__init__()
        self.controller = controller
        self.oled = oled
        self.text_file = text_file
        self.title("Train Controller UI")
        self.geometry("400x700")
        
        # Constants
        self.MPH_TO_MPS = 0.44704
        self.MPS_TO_MPH = 2.23694
        self.station_distance = float('inf')
        self.delta_position = 0
        self.beacon_data = {}
        
        # Station approach variables
        self.station_approach_active = False
        self.door_open_timer = None
        self.station_side = None
        self.arriving_station = None
        self.approaching_station = False
        
        # Initialize variables
        self.output_file = 'TC1_outputs.txt'
        self.last_modified_time = None
        self.failure_states = {
            'Brake_Fail': False,
            'Signal_Fail': False,
            'Engine_Fail': False
        }
        self.P_target = 50  
        self.P_actual = 0  
        self.current_speed = 0  
        self.current_authority = 100
        self.suggested_authority = 100
        self.suggested_speed = 0
        self.is_automatic_mode = False
        self.manual_eb_engaged = False

        # Initialize LEDs
        self.leds = {
            "service_brake": LED(26),
            "emergency_brake": LED(23),
            "left_door": LED(24),
            "right_door": LED(25),
            "out_light": LED(16),
            "cabin_light": LED(6),
            "ac": LED(5),
            "failure": LED(17)
        }

        # Setup UI
        self.create_widgets()
        
        # Initialize file monitoring
        try:
            self.last_modified_time = os.path.getmtime(self.text_file)
            self.read_train_outputs()
        except Exception as e:
            print(f"Initial file read error: {e}")

        # Start periodic updates
        self.update_power()
        self.after(1000, self.check_file_updates)

    def create_widgets(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame
        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, padx=10, pady=10)

        self.power_label = tk.Label(self.top_frame, text="Current Power: 0 kW", font=("Arial", 16))
        self.power_label.pack(pady=10)

        self.Kp_label = tk.Label(self.top_frame, text="Kp:", font=("Arial", 12))
        self.Kp_label.pack()
        self.Kp_entry = tk.Entry(self.top_frame, font=("Arial", 12))
        self.Kp_entry.pack()

        self.Ki_label = tk.Label(self.top_frame, text="Ki:", font=("Arial", 12))
        self.Ki_label.pack()
        self.Ki_entry = tk.Entry(self.top_frame, font=("Arial", 12))
        self.Ki_entry.pack()

        self.update_button = tk.Button(self.top_frame, text="Update Kp & Ki", command=self.update_gains)
        self.update_button.pack(pady=10)

        self.direct_mode_var = tk.IntVar()
        self.direct_mode_check = tk.Checkbutton(self.top_frame, text="Direct Power Mode", 
                                              variable=self.direct_mode_var, command=self.toggle_direct_mode)
        self.direct_mode_check.pack(pady=5)

        self.is_automatic_mode_button = tk.Button(self.top_frame, text="Toggle Automatic Mode", 
                                                command=self.toggle_automatic_mode)
        self.is_automatic_mode_button.pack(pady=10)

        # Bottom frame
        self.bottom_frame = tk.Frame(self.main_frame)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.current_authority_label = tk.Label(self.bottom_frame, text="Current Authority: 100", 
                                              font=("Arial", 12), anchor='w')
        self.current_authority_label.pack(pady=5, fill='x')

        self.current_speed_label = tk.Label(self.bottom_frame, text="Current Speed: 0 mph", 
                                         font=("Arial", 12), anchor='w')
        self.current_speed_label.pack(pady=5, fill='x')

        self.suggested_authority_label = tk.Label(self.bottom_frame, 
                                               text=f"Suggested Authority: {self.suggested_authority}", 
                                               font=("Arial", 12), anchor='w')
        self.suggested_authority_label.pack(pady=5, fill='x')

        self.suggested_speed_label = tk.Label(self.bottom_frame, 
                                           text=f"Suggested Speed: {self.suggested_speed} mph", 
                                           font=("Arial", 12), anchor='w')
        self.suggested_speed_label.pack(pady=5, fill='x')

        self.beacon_label = tk.Label(self.bottom_frame, text="Next Station: -- (-- m)", 
                                   font=("Arial", 12), anchor='w')
        self.beacon_label.pack(pady=5, fill='x')

        self.status_label = tk.Label(self.bottom_frame, text="Status: Normal", 
                                   font=("Arial", 12), anchor='w')
        self.status_label.pack(pady=10, fill='x')

        self.create_led_buttons()

    def create_led_buttons(self):
        buttons = [
            ("Toggle Service Brake", "service_brake"),
            ("Toggle Emergency Brake", "emergency_brake"),
            ("Toggle Left Door", "left_door"),
            ("Toggle Right Door", "right_door"),
            ("Toggle Outside Lights", "out_light"),
            ("Toggle Cabin Lights", "cabin_light"),
            ("Toggle Air Conditioning", "ac"),
            ("Toggle failure Indicator", "failure"),
        ]
        
        button_frame = tk.Frame(self.bottom_frame)
        button_frame.pack(pady=10)
        
        for i, (text, led_name) in enumerate(buttons):
            row = i // 2
            col = i % 2
            tk.Button(button_frame, text=text, command=lambda ln=led_name: self.toggle_led(ln)).grid(
                row=row, column=col, padx=5, pady=5, sticky='ew')

    def update_gains(self):
        try:
            Kp = float(self.Kp_entry.get())
            Ki = float(self.Ki_entry.get())
            self.controller.update_gains(Kp, Ki)
            self.update_status(f"Kp and Ki updated to: {Kp}, {Ki}")
        except ValueError:
            self.update_status("Error: Invalid input for Kp or Ki", is_error=True)

    def toggle_direct_mode(self):
        self.controller.set_direct_power_mode(self.direct_mode_var.get() == 1)
        mode = "Direct" if self.direct_mode_var.get() else "PI"
        self.update_status(f"Switched to {mode} Power Mode")

    def toggle_automatic_mode(self):
        self.is_automatic_mode = not self.is_automatic_mode
        color = "green" if self.is_automatic_mode else "red"
        self.is_automatic_mode_button.config(bg=color)
        mode = "Automatic" if self.is_automatic_mode else "Manual"
        self.update_status(f"Switched to {mode} Mode")
        self.update_ui()

    def read_train_outputs(self, file_path='train1_outputs.txt'):
        try:
            with open(file_path, 'r') as file:
                data = {}
                for line in file:
                    line = line.strip()
                    if line and ':' in line:
                        key, value = line.split(':', 1)
                        data[key.strip()] = value.strip()

            # Process basic values
            self.current_speed = float(data.get('Actual_Speed', 0))
            self.current_authority = float(data.get('Actual_Authority', 0))
            self.delta_position = float(data.get('Delta_Position', 0))

            # Process beacon data - handle dictionary string format
            beacon_str = data.get('Beacon', '{}').strip()
            self.beacon_data = {}
            self.station_distance = float('inf')
            
            try:
                # Remove curly braces if present
                if beacon_str.startswith('{') and beacon_str.endswith('}'):
                    beacon_str = beacon_str[1:-1]
                
                # Split into key-value pairs
                pairs = [pair.strip() for pair in beacon_str.split(',') if pair.strip()]
                
                # Process each pair
                for pair in pairs:
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        key = key.strip().strip("'\"")
                        value = value.strip().strip("'\"")
                        self.beacon_data[key] = value
                
                # Extract specific beacon information
                if 'station_distance' in self.beacon_data:
                    try:
                        self.station_distance = float(self.beacon_data['station_distance'])
                    except ValueError:
                        self.station_distance = float('inf')
                
                self.arriving_station = self.beacon_data.get('arriving_station', 'Unknown')
                self.station_side = self.beacon_data.get('station_side', 'unknown').lower()
                
                # Update beacon display
                beacon_text = f"Next Station: {self.arriving_station} ({self.station_distance:.1f}m, {self.station_side} side)"
                self.beacon_label.config(text=beacon_text)
                
                # Station approach sequence
                if not self.station_approach_active:
                    if 0 < self.station_distance <= 10 and self.current_speed > 0:
                        self.start_station_approach()
                    elif self.station_distance > 10 and self.station_approach_active:
                        self.cancel_station_approach()
                        
            except Exception as e:
                print(f"Error parsing beacon data: {e}")
                self.beacon_data = {}
                self.station_distance = float('inf')
                self.beacon_label.config(text="Next Station: -- (-- m)")
                self.cancel_station_approach()

            # Process failures
            self.failure_states = {
                'Brake_Fail': data.get('Brake_Fail', '0') == '1',
                'Signal_Fail': data.get('Signal_Fail', '0') == '1',
                'Engine_Fail': data.get('Engine_Fail', '0') == '1'
            }
            emergency_brake = data.get('Emergency_Brake', '0') == '1'
            any_failure = any(self.failure_states.values())

            # Update failure LED
            self.leds['failure'].on() if any_failure else self.leds['failure'].off()
            
            # Update emergency brake (only if not manually engaged)
            if not self.manual_eb_engaged:
                if emergency_brake or any_failure:
                    self.leds['emergency_brake'].on()
                    self.update_status("Emergency brake activated", is_error=True)
                else:
                    self.leds['emergency_brake'].off()

            # Process suggested speed/authority
            speed_auth = data.get('Suggested_Speed_Authority', '0000000000')
            if len(speed_auth) == 10 and all(bit in '01' for bit in speed_auth):
                msb = speed_auth[0]
                value = int(speed_auth[1:], 2)
                
                if msb == '0':
                    self.suggested_speed = value * 0.0625
                else:
                    self.suggested_authority = value

            self.update_ui()
            return True

        except Exception as e:
            print(f"Error reading train outputs: {e}")
            return False

    def start_station_approach(self):
        """Begin the station approach sequence"""
        self.station_approach_active = True
        self.leds['service_brake'].on()
        self.update_status(f"Approaching {self.arriving_station} - service brake activated")
        
        # Check every 100ms if we've stopped
        self.after(100, self.check_stopped_at_station)

    def check_stopped_at_station(self):
        """Check if train has stopped to begin door sequence"""
        if self.current_speed <= 0.1:  # Consider stopped below 0.1 mph
            self.handle_stopped_at_station()
        elif self.station_approach_active:
            self.after(100, self.check_stopped_at_station)

    def handle_stopped_at_station(self):
        """Handle the door opening/closing sequence"""
        # Open the correct door
        if self.station_side == 'left':
            self.leds['left_door'].on()
            door_led = 'left_door'
        else:  # Default to right side
            self.leds['right_door'].on()
            door_led = 'right_door'
        
        self.update_status(f"Stopped at {self.arriving_station} - {self.station_side} door opening")
        
        # Close door after 10 seconds
        if self.door_open_timer:
            self.after_cancel(self.door_open_timer)
        self.door_open_timer = self.after(10000, self.close_doors_and_depart)

    def close_doors_and_depart(self):
        """Close doors and prepare for departure"""
        # Close both doors (only one should be open)
        self.leds['left_door'].off()
        self.leds['right_door'].off()
        
        # Release service brake
        self.leds['service_brake'].off()
        self.station_approach_active = False
        self.door_open_timer = None
        
        self.update_status(f"Doors closed - ready to depart {self.arriving_station}")

    def cancel_station_approach(self):
        """Cancel any ongoing station approach sequence"""
        if self.station_approach_active:
            self.station_approach_active = False
            self.leds['service_brake'].off()
            if self.door_open_timer:
                self.after_cancel(self.door_open_timer)
                self.door_open_timer = None
            self.leds['left_door'].off()
            self.leds['right_door'].off()
            self.update_status("Station approach cancelled")

    def check_file_updates(self):
        try:
            current_modified_time = os.path.getmtime(self.text_file)
            if current_modified_time != self.last_modified_time:
                self.last_modified_time = current_modified_time
                if self.read_train_outputs():
                    self.update_status("Configuration updated from file")
        except Exception as e:
            print(f"File check error: {e}")
        
        self.after(1000, self.check_file_updates)

    def toggle_led(self, led_name):
        if self.is_automatic_mode:
            self.update_status("Cannot toggle LEDs in automatic mode", is_error=True)
            return
        
        led = self.leds.get(led_name)
        if led:
            led.toggle()
            state = "ON" if led.is_lit else "OFF"
            self.update_status(f"{led_name.replace('_', ' ').capitalize()} turned {state}")
            
            if led_name in ["left_door", "right_door"]:
                if self.P_actual > 0:
                    self.update_status("Warning: Cannot open doors while power > 0", is_error=True)
                    led.off()
                    return
                
                if led_name == "left_door" and led.is_lit:
                    self.leds["right_door"].off()
                elif led_name == "right_door" and led.is_lit:
                    self.leds["left_door"].off()
            
            elif led_name == "emergency_brake":
                self.manual_eb_engaged = led.is_lit
                if led.is_lit:
                    self.leds["service_brake"].off()
            
            elif led_name == "service_brake" and led.is_lit and self.leds["emergency_brake"].is_lit:
                led.off()
                self.update_status("Cannot engage service brake when emergency brake is active", is_error=True)
            
            elif led_name == "failure" and led.is_lit:
                self.leds["emergency_brake"].on()
                self.update_status("Failure detected! Emergency brake activated", is_error=True)
            
            self.update_ui()

    def update_ui(self):
        self.current_speed_label.config(text=f"Current Speed: {self.current_speed:.1f} mph")
        self.current_authority_label.config(text=f"Current Authority: {self.current_authority:.1f} m")
        self.suggested_speed_label.config(text=f"Suggested Speed: {self.suggested_speed:.1f} mph")
        self.suggested_authority_label.config(text=f"Suggested Authority: {self.suggested_authority} m")

        mode = "AUTO" if self.is_automatic_mode else "MANUAL"
        brake = "ON" if self.leds['service_brake'].is_lit else "OFF"
        emergency = "ON" if self.leds['emergency_brake'].is_lit else "OFF"
        failure = "ON" if self.leds['failure'].is_lit else "OFF"
        self.status_label.config(text=f"Status: Mode={mode} | Brake={brake} | Emerg={emergency} | Fail={failure}")

        # Add visual indication of station approach
        if self.station_approach_active:
            self.beacon_label.config(fg="red")
        else:
            self.beacon_label.config(fg="black")

    def update_status(self, message, is_error=False):
        if is_error:
            self.status_label.config(text=f"Status: ERROR - {message}", fg="red")
        else:
            self.status_label.config(text=f"Status: {message}", fg="black")
        self.update_idletasks()

    def update_power(self):
        if self.is_automatic_mode:
            self.apply_automatic_mode()

        service_brake = self.leds["service_brake"].is_lit
        emergency_brake = self.leds["emergency_brake"].is_lit

        current_speed_mps = self.current_speed * self.MPH_TO_MPS
        
        P_cmd = self.controller.compute_Pcmd(
            self.P_target,
            current_speed_mps,
            service_brake,
            emergency_brake
        )
        
        self.power_label.config(text=f"Current Power: {round(P_cmd, 2)} kW")
        self.P_actual = P_cmd
        self.update_oled(P_cmd)
        
        self.write_commanded_power(P_cmd)

        if self.suggested_authority == 0:
            if not self.leds["failure"].is_lit:
                self.leds["failure"].on()
                self.leds["emergency_brake"].on()
                self.update_status("Emergency Stop: Suggested authority is 0", is_error=True)

        self.after(1000, self.update_power)

    def write_commanded_power(self, power):
        try:
            with open(self.output_file, 'w') as f:
                f.write(f"Commanded_Power: {power:.2f}\n")
                f.write(f"Current_Speed: {self.current_speed:.2f}\n")
                f.write(f"Suggested_Speed: {self.suggested_speed:.2f}\n")
                f.write(f"Current_Authority: {self.current_authority}\n")
                f.write(f"Suggested_Authority: {self.suggested_authority}\n")
                f.write(f"Service_Brake: {'1' if self.leds['service_brake'].is_lit else '0'}\n")
                f.write(f"Emergency_Brake: {'1' if self.leds['emergency_brake'].is_lit else '0'}\n")
                f.write(f"Beacon: {str(self.beacon_data)}\n")
                f.write(f"Delta_Position: {self.delta_position}\n")
        except Exception as e:
            self.update_status(f"Error writing commanded power: {e}", is_error=True)

    def apply_automatic_mode(self):
        try:
            with open(self.text_file, "r") as file:
                lines = file.readlines()

            for line in lines:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                
                key, value = map(str.strip, line.split(":"))
                
                if key == "suggested_speed_authority":
                    binary_string = value
                    self.read_binary_string(binary_string)
                elif key == "service_brakes":
                    self.leds["service_brake"].value = (value.lower() == "on")
                elif key == "emergency_brakes":
                    self.leds["emergency_brake"].value = (value.lower() == "on")
                elif key == "left_door":
                    self.leds["left_door"].value = (value.lower() == "on")
                elif key == "right_door":
                    self.leds["right_door"].value = (value.lower() == "on")
                elif key == "outside_lights":
                    self.leds["out_light"].value = (value.lower() == "on")
                elif key == "cabin_lights":
                    self.leds["cabin_light"].value = (value.lower() == "on")
                elif key == "ac":
                    self.leds["ac"].value = (value.lower() == "on")
                elif key == "failure":
                    self.leds["failure"].value = (value.lower() == "on")

            self.update_ui()

        except FileNotFoundError:
            self.update_status("Error: Text file not found", is_error=True)
        except Exception as e:
            self.update_status(f"Error reading text file: {str(e)}", is_error=True)

    def read_binary_string(self, binary_string):
        if binary_string[0] == '0':
            self.suggested_speed = int(binary_string[1:], 2) * 0.0625
        elif binary_string[0] == '1':
            self.suggested_authority = int(binary_string[1:], 2)

        self.update_ui()

    def update_oled(self, P_cmd):
        image = Image.new("1", (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)

        draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)
        draw.text((10, 20), f"{round(P_cmd, 2)} kW", font=font, fill=255)

        self.oled.image(image)
        self.oled.show()

def setup_oled():
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
    oled.fill(0)
    oled.show()
    return oled

if __name__ == "__main__":
    oled = setup_oled()
    controller = PowerControl(P_max=120)
    app = train_controller_ui(controller, oled, 'train1_outputs.txt')
    app.mainloop()