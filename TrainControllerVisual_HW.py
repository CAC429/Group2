import tkinter as tk
from tkinter import messagebox
from gpiozero import LED
import time
import board
import busio
import adafruit_ssd1306
import csv
from PIL import Image, ImageDraw, ImageFont


class power_controller:
    def __init__(self, P_max):
        self.Kp = 0.5
        self.Ki = 0.1
        self.P_max = P_max
        self.integral = 0
        self.P_k_1 = 0

    def update_gains(self, Kp, Ki):
        self.Kp = Kp
        self.Ki = Ki

    def compute_Pcmd(self, P_target, P_actual, service_brake, emergency_brake, current_speed, mass=50000):
        if emergency_brake:
            deceleration = 2.73
        elif service_brake:
            deceleration = 1.2
        else:
            deceleration = 0

        braking_force = mass * deceleration
        power_reduction = braking_force / 1000

        if emergency_brake:
            self.P_k_1 = 0
            self.integral = 0
            return 0  

        error = P_target - P_actual
        self.integral += error
        P_cmd = self.P_k_1 + (self.Kp * error) + (self.Ki * self.integral)

        if service_brake:
            reduction_step = max(0, self.P_k_1 - (power_reduction * 0.35))
            P_cmd = max(0, reduction_step)
            self.integral = 0

        P_cmd = max(0, min(P_cmd, self.P_max))
        self.P_k_1 = P_cmd
        return P_cmd


class train_controller_ui(tk.Tk):
    def __init__(self, controller, oled, csv_file):
        super().__init__()
        self.controller = controller
        self.oled = oled
        self.csv_file = csv_file
        self.title("Train Controller UI")
        self.geometry("400x600")

        self.is_automatic_mode = False

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

        self.P_target = 50  
        self.P_actual = 0  
        self.current_speed = 0  

        self.create_widgets()
        self.update_power()

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

        self.is_automatic_mode_button = tk.Button(self, text="Toggle Automatic Mode", command=self.toggle_automatic_mode)
        self.is_automatic_mode_button.pack(pady=10)
        

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

            if self.leds["service_brake"].is_lit and self.leds["emergency_brake"].is_lit:
                self.leds["service_brake"].off()
                messagebox.showinfo("Info", "Service brake disabled because emergency brake is active")
            
            if led_name == "failure" and self.leds["failure"].is_lit:
                self.leds["emergency_brake"].on()
                messagebox.showinfo("Warning", "Failure detected! Emergency brake activated")
            
            self.update_ui()

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


    def toggle_automatic_mode(self):
        self.is_automatic_mode = not self.is_automatic_mode
        mode = "Automatic" if self.is_automatic_mode else "Manual"
        messagebox.showinfo("Mode Changed", f"Switched to {mode} Mode")
        self.update_ui()

    def update_ui(self):
        brake_status = "ON" if self.leds["service_brake"].is_lit else "OFF"
        emergency_status = "ON" if self.leds["emergency_brake"].is_lit else "OFF"
        failure_status = "ON" if self.leds["failure"].is_lit else "OFF"

        self.power_label.config(text=f"Mode: {'Automatic' if self.is_automatic_mode else 'Manual'} | Brake: {brake_status} | Emergency: {emergency_status} | Failure: {failure_status}")


    def update_power(self):
        if self.is_automatic_mode:
            self.apply_automatic_mode()

        service_brake = self.leds["service_brake"].is_lit
        emergency_brake = self.leds["emergency_brake"].is_lit

        P_cmd = self.controller.compute_Pcmd(self.P_target, self.P_actual, service_brake, emergency_brake, self.current_speed)
        self.power_label.config(text=f"Current Power: {round(P_cmd, 2)} kW")

        self.P_actual = P_cmd
        self.update_oled(P_cmd)

        self.after(1000, self.update_power)
    
    def apply_automatic_mode(self):
        try:
            with open(self.csv_file, mode='r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) == 2:
                        control_name, state = row
                        state = state.strip().lower()

                        # Handle control state toggling based on CSV data
                        if control_name == "service_brakes":
                            self.leds["service_brake"].on() if state == "on" else self.leds["service_brake"].off()
                        elif control_name == "emergency_brakes":
                            self.leds["emergency_brake"].on() if state == "on" else self.leds["emergency_brake"].off()
                        elif control_name == "left_door":
                            self.leds["left_door"].on() if state == "on" else self.leds["left_door"].off()
                        elif control_name == "right_door":
                            self.leds["right_door"].on() if state == "on" else self.leds["right_door"].off()
                        elif control_name == "outside_lights":
                            self.leds["out_light"].on() if state == "on" else self.leds["out_light"].off()
                        elif control_name == "cabin_lights":
                            self.leds["cabin_light"].on() if state == "on" else self.leds["cabin_light"].off()
                        elif control_name == "ac":
                            self.leds["ac"].on() if state == "on" else self.leds["ac"].off()
                        elif control_name == "failure":
                            self.leds["failure"].on() if state == "on" else self.leds["failure"].off()

            self.update_ui()
        except FileNotFoundError:
            messagebox.showerror("Error", "CSV file not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading CSV: {str(e)}")

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
    controller = power_controller(P_max=100)
    app = train_controller_ui(controller, oled, 'TestBench.csv')
    app.mainloop()
