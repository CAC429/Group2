#!/usr/bin/env python3
import lgpio
import time
import atexit
import json
import sys
import select
from PIL import Image, ImageDraw, ImageFont
import board
import busio
import adafruit_ssd1306

class LEDController:
    def __init__(self):
        # Hardware initialization flags
        self.hardware_initialized = True
        self.gpio_handle = None
        self.oled = None
        
        # Initialize GPIO
        try:
            self.gpio_handle = lgpio.gpiochip_open(0)
            print("GPIO chip opened successfully")
        except Exception as e:
            print(f"GPIO initialization failed: {str(e)} - Running in simulation mode")
            self.hardware_initialized = False

        self.pins = {
            "service_brake": 26,
            "emergency_brake": 23,
            "left_door": 24,
            "right_door": 25,
            "out_light": 16,
            "cabin_light": 6,
            "ac": 5,
            "failure": 17
        }

        # Initialize GPIO pins if hardware is available
        if self.hardware_initialized:
            for name, pin in self.pins.items():
                try:
                    # Try to free first (ignore errors)
                    try:
                        lgpio.gpio_free(self.gpio_handle, pin)
                    except:
                        pass
                    
                    # Claim as output
                    lgpio.gpio_claim_output(self.gpio_handle, pin)
                    lgpio.gpio_write(self.gpio_handle, pin, 0)
                    print(f"GPIO {pin} ({name}) initialized successfully")
                except Exception as e:
                    print(f"Warning: Could not initialize {name} (GPIO {pin}): {str(e)}")
                    self.pins[name] = None  # Mark pin as unavailable

        # Initialize OLED display
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
            self.oled.fill(0)
            self.oled.show()
            print("OLED display initialized successfully")
        except Exception as e:
            print(f"OLED initialization failed: {str(e)}")
            self.oled = None

        atexit.register(self.cleanup)

    def update_oled(self, power):
        """Update OLED display with power value"""
        if self.oled:
            try:
                image = Image.new("1", (self.oled.width, self.oled.height))
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
                draw.text((10, 20), f"{power:.2f} kW", font=font, fill=255)
                self.oled.image(image)
                self.oled.show()
            except Exception as e:
                print(f"OLED update error: {str(e)}")

    def cleanup(self):
        """Clean up resources"""
        if self.hardware_initialized and self.gpio_handle:
            for name, pin in self.pins.items():
                if pin is not None:  # Only cleanup initialized pins
                    try:
                        lgpio.gpio_write(self.gpio_handle, pin, 0)
                        lgpio.gpio_free(self.gpio_handle, pin)
                    except:
                        pass  # Silent cleanup
            
            try:
                lgpio.gpiochip_close(self.gpio_handle)
            except:
                pass

        if self.oled:
            try:
                self.oled.fill(0)
                self.oled.show()
            except:
                pass

def main():
    controller = LEDController()
    print("Hardware controller ready - waiting for commands...")
    
    try:
        while True:
            if select.select([sys.stdin], [], [], 0.1)[0]:
                line = sys.stdin.readline()
                if not line:
                    break
                    
                try:
                    command = json.loads(line.strip())
                    print(f"Received command: {command}")
                    
                    if 'power' in command:
                        controller.update_oled(command['power'])
                        
                    if 'leds' in command and controller.hardware_initialized:
                        for led, state in command['leds'].items():
                            if led in controller.pins and controller.pins[led] is not None:
                                lgpio.gpio_write(controller.gpio_handle, 
                                                controller.pins[led], 
                                                1 if state else 0)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON: {str(e)}")
                except Exception as e:
                    print(f"Command error: {str(e)}")
                    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        controller.cleanup()

if __name__ == "__main__":
    main()