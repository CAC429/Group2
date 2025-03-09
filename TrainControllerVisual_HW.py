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
        """Updates the PI gains dynamically"""
        self.Kp = Kp
        self.Ki = Ki

    def compute_Pcmd(self, P_target, P_actual):
        """Computes the commanded power P_k^cmd using a PI control law."""
        
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


def read_test_bench(file_path='TestBench.csv'):
    '''Reads and prints the contents of the CSV file'''
    data = {}
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Skips the header row if present
            print(f"Headers: {headers}")
            for row in csv_reader:
                utility, state = row
                data[utility] = state
        return data  # Indicates successful reading of the file
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def process_data(data, controller, sbrake_led, ebrake_led, left_door_led, right_door_led, out_light_led, cabin_light_led, ac_led, problem_led, oled, image, draw, font):
    '''Process the data passed as a parameter'''
    print("Processing CSV data...")

    P_target = 0
    P_actual = 0

    for utility, state in data.items():
        match utility:
            case "Authority":
                print(f"Authority: {state} units")

            case "Current_speed":
                print(f"Current speed: {state} mph")

            case "Service_brakes":                
                if state == "on":
                    print("Turning on service brakes (LED on)")                    
                    if ebrake_led.on():
                        sbrake_led.off()
                        print("both service and E brake cannot be on at same time!")
                        problem_led.on()
                    sbrake_led.on()
                elif state == "off":
                    print("Turning off service brakes (LED off)")
                    sbrake_led.off()

            case "Emergency_brakes":                
                if state == "on":
                    print("Turning on emergency brakes (LED on)")
                    ebrake_led.on()
                    if sbrake_led.on():
                        sbrake_led.off()
                        print("both service and E brake cannot be on at same time!")
                        problem_led.on()
                elif state == "off":
                    print("Turning off emergency brakes (LED off)")
                    ebrake_led.off()

            case "left_door_led":                
                if state == "on":
                    print("Opening left doors (LED on)")
                    left_door_led.on()
                elif state == "off":
                    print("Closing left doors (LED off)")       
                    left_door_led.off()     

            case "right_door_led":
                if state == "on":
                    print("Opening right doors (LED on)")
                    right_door_led.on()
                elif state == "off":
                    print("Closing right doors (LED off)")
                    right_door_led.off()

            case "Outside_lights":
                if state == "on":
                    print("Turning on outside lights (LED on)")
                    out_light_led.on()
                elif state == "off":
                    print("Turning off outside lights (LED off)")
                    out_light_led.off()

            case "Cabin_lights":
                if state == "on":
                    print("Turning on cabin lights (LED on)")
                    cabin_light_led.on()
                elif state == "off":
                    print("Turning off cabin lights (LED off)")
                    cabin_light_led.off()

            case "Air_conditioning":
                if state == "on":
                    print("Turning on air conditioning")
                    ac_led.on()
                elif state == "off":
                    print("Turning off AC")
                    ac_led.off()
            case "Cabin_temp":
                print(f"Cabin temp: {state} degrees f")
                if (int(state) > 70):
                    ac_led.on()
                    print("Turning on air conditioning")
                    
            case "Problem":
                if state == "on":
                    print ("There is a problem")
                    problem_led.on()
                elif state == "off":
                    print("No problem")
                    problem_led.off()

            case "Kp":
                try:
                    Kp = float(state)
                    controller.update_gains(Kp, controller.Ki)
                except ValueError:
                    print(f"Invalid value for Kp: {state}")

            case "Ki":
                try:
                    Ki = float(state)
                    controller.update_gains(controller.Kp, Ki)
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

        

    # Compute P_k^cmd using the controller
    P_cmd = controller.compute_Pcmd(P_target, P_actual)
    print(f"Computed P_k^cmd: {P_cmd} kW")

    # Clear the OLED display
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    # Display computed power
    draw.text((1, 10), f"{round(P_cmd, 3)} kW", font=font, fill=255)

    # Update OLED screen
    oled.image(image)
    oled.show()

    # Delay before clearing the display
    time.sleep(2)
    oled.fill(0)
    oled.show()

##############################################################################################
''' 
notes 3/9/25

need to disp next station
    need to either have a list of stations or get the "next stop" from someone

need to automatic brake 
    figure out distance between stations and when at x distance, start braking

need to open the corresponding door for each station
    either just told which side to open or have the list of stations with sides
    also direction of car 

    

'''
##############################################################################################


def main():
    sbrake_led = LED(26)  # Service brakes
    ebrake_led = LED(23)  # Emergency brakes
    left_door_led = LED(24)  # Left door
    right_door_led = LED(25)  # Right door
    out_light_led = LED(16)  # Outside lights
    cabin_light_led = LED(6)   # Cabin lights
    ac_led = LED(5)   # Air conditioning
    problem_led = LED(17)  # Problem

    # Initialize I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Initialize the OLED display (128x64 pixels)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

    # Clear the screen
    oled.fill(0)
    oled.show()

    # Create a blank image for drawing
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Load a larger font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
    except IOError:
        font = ImageFont.load_default()

    # Create the power controller with max power limit
    controller = PowerController(P_max=100)

    while True:
        csv_data = read_test_bench()
        if csv_data is not None:
            process_data(csv_data, controller, sbrake_led, ebrake_led, left_door_led, right_door_led, out_light_led, cabin_light_led, ac_led, problem_led, oled, image, draw, font)
        else:
            print("Failed to read CSV file")
        sleep(1)


if __name__ == "__main__":
    main()
