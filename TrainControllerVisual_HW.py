from gpiozero import LED
import time
from time import sleep
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import csv


class PowerController:
    def __init__(self, P_max):
        self.Kp = 0.0       # Proportional gain (default)
        self.Ki = 0.0       # Integral gain (default)
        self.P_max = P_max  # Maximum power constraint
        self.integral = 0   # Integral term
        self.P_k_1 = 0      # Previous power command

    def update_gains(self, Kp, Ki):
        "Updates the PI gains dynamically"
        self.Kp = Kp
        self.Ki = Ki

    def compute_Pcmd(self, P_target, P_actual):
        "Computes the commanded power P_k^cmd using a PI control law."
        
        # Compute error
        error = P_target - P_actual
        
        # Update integral term
        self.integral += error
        
        # Compute raw commanded power using PI control law
        P_cmd = self.P_k_1 + (self.Kp * error) + (self.Ki * self.integral)

        # Limit to P_max constraint
        P_cmd = min(P_cmd, self.P_max)

        # Store previous commanded power
        self.P_k_1 = P_cmd
        
        return P_cmd


class DataProcessor:
    def __init__(self, controller, oled, image, draw, font, leds):
        self.controller = controller
        self.oled = oled
        self.image = image
        self.draw = draw
        self.font = font
        self.leds = leds

    def process_data(self, data):
        "Process the data passed as a parameter"
        print("Processing CSV data...")

        P_target = 0
        P_actual = 0

        for utility, state in data.items():
            match utility:
                case "Authority":
                    print(f"Authority: {state} km")
                case "Current_speed":
                    print(f"Current speed: {state} mph")
                case "Service_brakes":
                    self.handle_brakes(state, "service")
                case "Emergency_brakes":
                    self.handle_brakes(state, "emergency")
                case "left_door_led":
                    self.toggle_led("left_door", state)
                case "right_door_led":
                    self.toggle_led("right_door", state)
                case "Outside_lights":
                    self.toggle_led("out_light", state)
                case "Cabin_lights":
                    self.toggle_led("cabin_light", state)
                case "Air_conditioning":
                    self.toggle_led("ac", state)
                case "Cabin_temp":
                    if int(state) > 70:
                        self.leds["ac"].on()
                        print("Turning on air conditioning")
                case "Problem":
                    self.toggle_led("problem", state)
                case "Kp":
                    try:
                        self.controller.update_gains(float(state), self.controller.Ki)
                    except ValueError:
                        print(f"Invalid value for Kp: {state}")
                case "Ki":
                    try:
                        self.controller.update_gains(self.controller.Kp, float(state))
                    except ValueError:
                        print(f"Invalid value for Ki: {state}")
                case "P_target":
                    try:
                        P_target = float(state)
                    except ValueError:
                        print(f"Invalid value for P_target: {state}")
                case "P_actual":
                    try:
                        P_actual = float(state)
                    except ValueError:
                        print(f"Invalid value for P_actual: {state}")
        
        P_cmd = self.controller.compute_Pcmd(P_target, P_actual)
        print(f"Computed P_k^cmd: {P_cmd} kW")
        
        self.display_power(P_cmd)

    def handle_brakes(self, state, brake_type):
        brake_led = self.leds[f"{brake_type}_brake"]
        if state == "on":
            print(f"Turning on {brake_type} brakes (LED on)")
            brake_led.on()

            # If both brakes are on, service brake turns off and problem activated
            if self.leds["service_brake"].is_lit and self.leds["emergency_brake"].is_lit:
                print("Conflict: Both brakes are on! Turning off service brake")
                self.leds["service_brake"].off()
                self.leds["problem"].on()

        else:
            print(f"Turning off {brake_type} brakes (LED off)")
            brake_led.off()

    def toggle_led(self, led_name, state):
        if state == "on":
            print(f"Turning on {led_name} (LED on)")
            self.leds[led_name].on()
        else:
            print(f"Turning off {led_name} (LED off)")
            self.leds[led_name].off()

    def display_power(self, P_cmd):
        self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)
        self.draw.text((1, 10), f"{round(P_cmd, 3)} kW", font=self.font, fill=255)
        self.oled.image(self.image)
        self.oled.show()
        time.sleep(2)
        self.oled.fill(0)
        self.oled.show()


def read_test_bench(file_path='TestBench.csv'):
    data = {}
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Skips the header row if present
            print(f"Headers: {headers}")
            for row in csv_reader:
                utility, state = row
                data[utility] = state
        return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def main():
    leds = {
        "service_brake": LED(26),
        "emergency_brake": LED(23),
        "left_door": LED(24),
        "right_door": LED(25),
        "out_light": LED(16),
        "cabin_light": LED(6),
        "ac": LED(5),
        "problem": LED(17)
    }

    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
    oled.fill(0)
    oled.show()
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)

    controller = PowerController(P_max=100)
    processor = DataProcessor(controller, oled, image, draw, font, leds)

    while True:
        csv_data = read_test_bench()
        if csv_data:
            processor.process_data(csv_data)
        sleep(1)


if __name__ == "__main__":
    main()
