import tkinter as tk
from tkinter import messagebox
import threading
import csv
from gpiozero import LED
import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

class PowerController:
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

class PowerControllerUI(tk.Tk):
    def __init__(self, controller, oled):
        super().__init__()
        self.controller = controller
        self.oled = oled
        self.title("Power Controller UI")
        self.geometry("400x550")
        self.automatic_mode = False

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

        self.auto_mode_button = tk.Button(self, text="Toggle Automatic Mode", command=self.toggle_automatic_mode)
        self.auto_mode_button.pack(pady=10)

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
            ("Toggle Failure Indicator", "failure"),
        ]
        
        for text, led_name in buttons:
            tk.Button(self, text=text, command=lambda ln=led_name: self.toggle_led(ln)).pack(pady=5)

    def toggle_automatic_mode(self):
        self.automatic_mode = not self.automatic_mode
        mode = "ON" if self.automatic_mode else "OFF"
        messagebox.showinfo("Automatic Mode", f"Automatic mode turned {mode}")
        if self.automatic_mode:
            threading.Thread(target=self.read_csv_continuously, daemon=True).start()

    def read_csv_continuously(self):
        while self.automatic_mode:
            self.read_csv_update()
            time.sleep(1)

    def read_csv_update(self):
        try:
            with open("TestBench.csv", mode="r", newline="", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                next(csv_reader)
                for row in csv_reader:
                    if row[0] in self.leds:
                        self.toggle_led(row[0])
        except FileNotFoundError:
            messagebox.showerror("Error", "CSV file not found!")

    def update_power(self):
        service_brake = self.leds["service_brake"].is_lit
        emergency_brake = self.leds["emergency_brake"].is_lit

        P_cmd = self.controller.compute_Pcmd(self.P_target, self.P_actual, service_brake, emergency_brake, self.current_speed)
        self.power_label.config(text=f"Current Power: {round(P_cmd, 2)} kW")
        self.P_actual = P_cmd
        self.update_oled(P_cmd)
        self.after(1000, self.update_power)

    def update_oled(self, P_cmd):
        image = Image.new("1", (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
        draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)
        draw.text((10, 20), f"{round(P_cmd, 2)} kW", font=font, fill=255)
        self.oled.image(image)
        self.oled.show()

if __name__ == "__main__":
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, busio.I2C(board.SCL, board.SDA))
    oled.fill(0)
    oled.show()
    controller = PowerController(P_max=100)
    app = PowerControllerUI(controller, oled)
    app.mainloop()
