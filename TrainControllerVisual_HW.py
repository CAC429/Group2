from gpiozero import LED
import time
from time import sleep
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import csv


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


def process_data(data, led1, led2, led3, led4, led5, led6, led7, led8, oled, image, draw, font):
    '''Process the data passed as a parameter'''
    print("Processing CSV data...")

    # Initialize Kp and Ki to avoid reference errors
    kp = 0.0
    ki = 0.0

    for utility, state in data.items():
        match utility:
            case "Service_brakes":                
                if state == "on":
                    print("Turning on service brakes (LED on)")
                    led1.on()
                elif state == "off":
                    print("Turning off service brakes (LED off)")
                    led1.off()

            case "Emergency_brakes":                
                if state == "on":
                    print("Turning on emergency brakes (LED on)")
                    led2.on()
                elif state == "off":
                    print("Turning off emergency brakes (LED off)")
                    led2.off()

            case "Left_door":                
                if state == "on":
                    print("Opening left doors (LED on)")
                    led3.on()
                elif state == "off":
                    print("Closing left doors (LED off)")       
                    led3.off()     

            case "Right_door":
                if state == "on":
                    print("Opening right doors (LED on)")
                    led4.on()
                elif state == "off":
                    print("Closing right doors (LED off)")
                    led4.off()

            case "Outside_lights":
                if state == "on":
                    print("Turning on outside lights (LED on)")
                    led5.on()
                elif state == "off":
                    print("Turning off outside lights (LED off)")
                    led5.off()

            case "Cabin_lights":
                if state == "on":
                    print("Turning on cabin lights (LED on)")
                    led6.on()
                elif state == "off":
                    print("Turning off cabin lights (LED off)")
                    led6.off()

            case "Air_conditioning":
                if state == "on":
                    print("Turning on air conditioning")
                    led7.on()
                elif state == "off":
                    print("Turning off AC")
                    led7.off()
            case "Problem":
                if state == "on":
                    print ("There is a problem")
                    led8.on()
                elif state == "off":
                    print("No problem")
                    led8.off()

            case "Kp":
                try:
                    kp = float(state)
                except ValueError:
                    print(f"Invalid value for Kp: {state}")

            case "Ki":
                try:
                    ki = float(state)
                except ValueError:
                    print(f"Invalid value for Ki: {state}")

            case "Speed":
                speed = float(state)
                if speed == 0:
                    power = 0  # Avoid division by zero
                else:
                    power = kp + (ki / speed)

                print(f"Calculated Power: {power} kW")

                # Clear the previous text
                draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

                # Draw new text
                draw.text((1, 10), str(round(power, 2))+ "kW ", font=font, fill=255)

                # Display image on OLED
                oled.image(image)
                oled.show()

                # Wait for a few seconds
                time.sleep(2)

                # Clear the display after 5 seconds
                oled.fill(0)
                oled.show()
                
                
    
def main():
    led1 = LED(26)  # Service brakes
    led2 = LED(23)  # Emergency brakes
    led3 = LED(24)  # Left door
    led4 = LED(25)  # Right door
    led5 = LED(16)  # Outside lights
    led6 = LED(6)   # Cabin lights
    led7 = LED(5)   # Air conditioning
    led8 = LED(17)  # Problem

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
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)  # Adjust font size as needed
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font if TTF is not found

    while True:
        csv_data = read_test_bench()
        if csv_data is not None:
            process_data(csv_data, led1, led2, led3, led4, led5, led6, led7, led8, oled, image, draw, font)
        else:
            print("Failed to read CSV file")
        sleep(1)


if __name__ == "__main__":
    main()
