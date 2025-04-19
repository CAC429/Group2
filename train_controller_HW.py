import argparse
import time
from gpiozero import LED
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

class LEDController:
    def __init__(self):
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
        
        # Initialize OLED
        i2c = busio.I2C(board.SCL, board.SDA)
        self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        self.oled.fill(0)
        self.oled.show()
        
        # Current power value
        self.current_power = 0

    def update_led(self, led_name, state):
        if led_name in self.leds:
            self.leds[led_name].on() if state else self.leds[led_name].off()

    def update_oled(self, power=None):
        if power is not None:
            self.current_power = power
            
        image = Image.new("1", (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)

        draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)
        draw.text((10, 20), f"{round(self.current_power, 2)} kW", font=font, fill=255)

        self.oled.image(image)
        self.oled.show()

    def process_command(self, args):
        # Update LEDs based on command line arguments
        for led_name in self.leds.keys():
            state = getattr(args, led_name, None)
            if state is not None:
                self.update_led(led_name, state)
        
        # Update power display if provided
        if args.power is not None:
            self.update_oled(args.power)
        
        return "LED states updated successfully"

def main():
    controller = LEDController()
    
    parser = argparse.ArgumentParser(description='Control train LEDs and display')
    parser.add_argument('--power', type=float, help='Set power display value')
    
    # Add arguments for each LED
    for led_name in controller.leds.keys():
        parser.add_argument(f'--{led_name}', type=int, choices=[0, 1], 
                          help=f'Set {led_name} state (0=off, 1=on)')
    
    args = parser.parse_args()
    
    result = controller.process_command(args)
    print(result)

if __name__ == "__main__":
    main()