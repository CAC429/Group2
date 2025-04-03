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


class PowerControl:
    def __init__(self, P_max=120, T=0.1):
        self.Kp = 0.0
        self.Ki = 0.0
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

        # Initialize variables first
        self.output_file = 'TC_outputs.txt'
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

        # Initialize LEDs after variables
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

    def read_train_outputs(self, file_path='TestBench.txt'):
            try:
                with open(file_path, 'r') as file:
                    data = {}
                    for line in file:
                        line = line.strip()
                        if line and ':' in line:
                            key, value = line.split(':', 1)
                            data[key.strip()] = value.strip()

                # Process actual values
                self.current_speed = float(data.get('Actual_Speed', 0)) * 2.23694  # m/s to mph
                self.current_authority = float(data.get('Actual_Authority', 0))

                # Process failure states
                failures = {
                    'Brake_Fail': data.get('Brake_Fail', '0') == '1',
                    'Signal_Fail': data.get('Signal_Fail', '0') == '1',
                    'Engine_Fail': data.get('Engine_Fail', '0') == '1'
                }
                emergency_brake = data.get('Emergency_Brake', '0') == '1'
                any_failure = any(failures.values())

                # Control LEDs based on states
                self.leds['failure'].on() if any_failure else self.leds['failure'].off()
                self.leds['emergency_brake'].on() if (emergency_brake or any_failure) else self.leds['emergency_brake'].off()
                
                # Turn off service brake if emergency brake is on
                if self.leds['emergency_brake'].is_lit and self.leds['service_brake'].is_lit:
                    self.leds['service_brake'].off()

                # Process suggested speed/authority from binary string
                speed_auth = data.get('Suggested_Speed_Authority', '0000000000')
                if len(speed_auth) == 10 and all(bit in '01' for bit in speed_auth):
                    msb = speed_auth[0]  # Most significant bit determines type
                    value = int(speed_auth[1:], 2)  # Convert remaining 9 bits to decimal
                    
                    if msb == '0':  # Speed command
                        # Convert binary value to mph (0.0625 mph per bit)
                        self.suggested_speed = value * 0.0625
                        print(f"Suggested speed set to: {self.suggested_speed:.2f} mph")
                    else:  # Authority command
                        self.suggested_authority = value  # Direct value in meters
                        print(f"Suggested authority set to: {self.suggested_authority} m")

                # Update all UI elements
                self.update_ui()
                return True

            except Exception as e:
                print(f"Error reading train outputs: {e}")
                return False


    def check_file_updates(self):
        """Check for file changes every second"""
        try:
            current_modified_time = os.path.getmtime(self.text_file)
            if current_modified_time != self.last_modified_time:
                self.last_modified_time = current_modified_time
                self.read_train_outputs()
        except Exception as e:
            print(f"File check error: {e}")
        
        # Schedule next check
        self.after(1000, self.check_file_updates)

    def create_widgets(self):
        self.power_label = tk.Label(self, text="Current Power: 0 kW", font=("Arial", 16))
        self.power_label.pack(pady=10)

        self.Kp_label = tk.Label(self, text="Kp:", font=("Arial", 12))
        self.Kp_label.pack()
        self.Kp_entry = tk.Entry(self, font=("Arial", 12))
        self.Kp_entry.pack()

        self.Ki_label = tk.Label(self, text="Ki:", font=("Arial", 12))
        self.Ki_label.pack()
        self.Ki_entry = tk.Entry(self, font=("Arial", 12))
        self.Ki_entry.pack()

        self.update_button = tk.Button(self, text="Update Kp & Ki", command=self.update_gains)
        self.update_button.pack(pady=10)

        self.direct_mode_var = tk.IntVar()
        self.direct_mode_check = tk.Checkbutton(self, text="Direct Power Mode", variable=self.direct_mode_var,
                                              command=self.toggle_direct_mode)
        self.direct_mode_check.pack(pady=5)

        self.is_automatic_mode_button = tk.Button(self, text="Toggle Automatic Mode", command=self.toggle_automatic_mode)
        self.is_automatic_mode_button.pack(pady=10)

        # Current Authority and Speed Labels
        self.current_authority_label = tk.Label(self, text="Current Authority: 100", font=("Arial", 12))
        self.current_authority_label.pack(pady=5)

        self.current_speed_label = tk.Label(self, text="Current Speed: 0 mph", font=("Arial", 12))
        self.current_speed_label.pack(pady=5)

        # Suggested Authority and Speed Labels (Read-only)
        self.suggested_authority_label = tk.Label(self, text=f"Suggested Authority: {self.suggested_authority}", font=("Arial", 12))
        self.suggested_authority_label.pack(pady=5)

        self.suggested_speed_label = tk.Label(self, text=f"Suggested Speed: {self.suggested_speed} mph", font=("Arial", 12))
        self.suggested_speed_label.pack(pady=5)

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
        
        for text, led_name in buttons:
            tk.Button(self, text=text, command=lambda ln=led_name: self.toggle_led(ln)).pack(pady=5)

    def toggle_direct_mode(self):
        self.controller.set_direct_power_mode(self.direct_mode_var.get() == 1)
        mode = "Direct" if self.direct_mode_var.get() else "PI"
        messagebox.showinfo("Info", f"Switched to {mode} Power Mode")

    def read_train_outputs(self, file_path='TestBench.txt'):
        try:
            with open(file_path, 'r') as file:
                data = {}
                for line in file:
                    line = line.strip()
                    if line and ':' in line:
                        key, value = line.split(':', 1)
                        data[key.strip()] = value.strip()

            # Process actual values
            self.current_speed = float(data.get('Actual_Speed', 0)) * 2.23694  # m/s to mph
            self.current_authority = float(data.get('Actual_Authority', 0))

            # Process failure states
            failures = {
                'Brake_Fail': data.get('Brake_Fail', '0') == '1',
                'Signal_Fail': data.get('Signal_Fail', '0') == '1',
                'Engine_Fail': data.get('Engine_Fail', '0') == '1'
            }
            emergency_brake = data.get('Emergency_Brake', '0') == '1'
            any_failure = any(failures.values())

            # Control LEDs based on states
            self.leds['failure'].on() if any_failure else self.leds['failure'].off()
            self.leds['emergency_brake'].on() if (emergency_brake or any_failure) else self.leds['emergency_brake'].off()
            
            if self.leds['emergency_brake'].is_lit and self.leds['service_brake'].is_lit:
                self.leds['service_brake'].off()

            # Process suggested speed/authority - flexible bit length handling
            speed_auth = data.get('Suggested_Speed_Authority', '0')
            
            if speed_auth and all(bit in '01' for bit in speed_auth):
                # Get type bit (first bit) and value bits (remaining bits)
                type_bit = speed_auth[0] if len(speed_auth) >= 1 else '0'
                value_bits = speed_auth[1:] if len(speed_auth) > 1 else '0'
                
                # Convert value bits to decimal (minimum 0, maximum 511 for 9 bits)
                value = int(value_bits, 2) if value_bits else 0
                
                if type_bit == '0':  # Speed command
                    self.suggested_speed = value * 0.0625  # 0.0625 mph per bit
                    print(f"Suggested speed: {value_bits} -> {value} -> {self.suggested_speed:.2f} mph")
                else:  # Authority command
                    self.suggested_authority = value  # 1 meter per bit
                    print(f"Suggested authority: {value_bits} -> {value} meters")
            else:
                print(f"Invalid binary string: {speed_auth}")
                # Default to current values if invalid
                self.suggested_speed = self.current_speed
                self.suggested_authority = self.current_authority

            # Update UI with all values
            self.update_ui()
            return True

        except Exception as e:
            print(f"Error reading train outputs: {e}")
            return False


    def update_gains(self):
        try:
            Kp = float(self.Kp_entry.get())
            Ki = float(self.Ki_entry.get())
            self.controller.update_gains(Kp, Ki)
            messagebox.showinfo("Info", f"Kp and Ki updated to: {Kp}, {Ki}")
        except ValueError:
            messagebox.showerror("Error", "Invalid input for Kp or Ki. Please enter numeric values.")

    def toggle_led(self, led_name):
        if self.is_automatic_mode:
            return
        
        led = self.leds.get(led_name)
        if led:
            if led.is_lit:
                led.off()
                state = "OFF"
            else:
                led.on()
                state = "ON"
            
            messagebox.showinfo("Info", f"{led_name.replace('_', ' ').capitalize()} turned {state}")
            
            if led_name in ["left_door", "right_door"] and self.P_actual > 0:
                messagebox.showwarning("Warning", "Cannot open doors while power > 0")
                return
            
            if led_name in ["left_door", "right_door"] and self.P_actual > 0:
                messagebox.showwarning("Warning", "Cannot open doors while power > 0, Failure triggered")
                self.leds["failure"].on()
                self.leds["emergency_brake"].on()
                messagebox.showwarning("Warning", "Failure detected! Emergency brake activated")
                self.update_ui()
                return 
            
            if led_name == "left_door" and self.leds["right_door"].is_lit:
                self.leds["right_door"].off()
            elif led_name == "right_door" and self.leds["left_door"].is_lit:
                self.leds["left_door"].off()

            if self.leds["service_brake"].is_lit and self.leds["emergency_brake"].is_lit:
                self.leds["service_brake"].off()
                messagebox.showinfo("Info", "Service brake disabled because emergency brake is active")
            
            if led_name == "failure" and self.leds["failure"].is_lit:
                self.leds["emergency_brake"].on()
                messagebox.showinfo("Warning", "Failure detected! Emergency brake activated")
            
            self.update_ui()


    def write_commanded_power(self, power):
        """Write the commanded power to output file"""
        try:
            with open(self.output_file, 'w') as f:
                f.write(f"Commanded_Power: {power:.2f}\n")
                f.write(f"Current_Speed: {self.current_speed:.2f}\n")
                f.write(f"Suggested_Speed: {self.suggested_speed:.2f}\n")
                f.write(f"Current_Authority: {self.current_authority}\n")
                f.write(f"Suggested_Authority: {self.suggested_authority}\n")
                f.write(f"Service_Brake: {'1' if self.leds['service_brake'].is_lit else '0'}\n")
                f.write(f"Emergency_Brake: {'1' if self.leds['emergency_brake'].is_lit else '0'}\n")
        except Exception as e:
            print(f"Error writing commanded power: {e}")

    def toggle_automatic_mode(self):
        self.is_automatic_mode = not self.is_automatic_mode
        color = "green" if self.is_automatic_mode else "red"
        self.is_automatic_mode_button.config(bg=color)
        mode = "Automatic" if self.is_automatic_mode else "Manual"
        messagebox.showinfo("Mode Changed", f"Switched to {mode} Mode")
        self.update_ui()

    def update_ui(self):
        """Update all UI elements with current values"""
        # Update status bar
        mode = "AUTO" if self.is_automatic_mode else "MANUAL"
        brake = "ON" if self.leds['service_brake'].is_lit else "OFF"
        emergency = "ON" if self.leds['emergency_brake'].is_lit else "OFF"
        failure = "ON" if self.leds['failure'].is_lit else "OFF"
        self.power_label.config(text=f"Mode: {mode} | Brake: {brake} | Emergency: {emergency} | Failure: {failure}")

        # Update numerical displays
        self.current_speed_label.config(text=f"Current Speed: {self.current_speed:.1f} mph")
        self.current_authority_label.config(text=f"Current Authority: {self.current_authority} m")
        self.suggested_speed_label.config(text=f"Suggested Speed: {self.suggested_speed:.1f} mph")
        self.suggested_authority_label.config(text=f"Suggested Authority: {self.suggested_authority} m")

        # Force UI refresh
        self.update_idletasks()


    def update_power(self):
        if self.is_automatic_mode:
            self.apply_automatic_mode()

        service_brake = self.leds["service_brake"].is_lit
        emergency_brake = self.leds["emergency_brake"].is_lit

        # Convert speed to m/s for power calculation
        current_speed_mps = self.current_speed * 0.44704
        
        P_cmd = self.controller.compute_Pcmd(
            self.P_target,
            current_speed_mps,
            service_brake,
            emergency_brake
        )
        
        self.power_label.config(text=f"Current Power: {round(P_cmd, 2)} kW")
        self.P_actual = P_cmd
        self.update_oled(P_cmd)
        
        # Write commanded power to file
        self.write_commanded_power(P_cmd)

        if self.suggested_authority == 0:
            if not self.leds["failure"].is_lit:
                self.leds["failure"].on()
                self.leds["emergency_brake"].on()
                messagebox.showwarning("Emergency Stop", "Suggested authority is 0 - Emergency brake activated")

        self.after(1000, self.update_power)
  

    def apply_automatic_mode(self):
        try:
            with open(self.text_file, "r") as file:
                lines = file.readlines()

            for line in lines:
                line = line.strip()
                if not line or ":" not in line:
                    continue  # Skip empty or malformed lines
                
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
            messagebox.showerror("Error", "Text file not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading text file: {str(e)}")

    def read_binary_string(self, binary_string):
        if binary_string[0] == '0':  # Suggested speed
            self.suggested_speed = int(binary_string[1:], 2) * 0.0625  # Convert to mph
        elif binary_string[0] == '1':  # Suggested authority
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
    app = train_controller_ui(controller, oled, 'TestBench.txt')
    app.mainloop()