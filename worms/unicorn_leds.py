import builtins
import time

from worms.led import Led
from worms.logos import vopak_logo

class UnicornLeds:
    def __init__(self, graphics, stellar, fps=60, min_brightness=0.1, start_brightness=0.5):
        self.pen_map = {}
        self.graphics = graphics
        self.stellar = stellar
        self.fps = fps  # Lower is slower
        self.tfps = 1000 // fps
        self.max_fps = 200
        self.uni_width, self.uni_height = graphics.get_bounds()
        self.leds = []
        self.leds_map = []
        self.deteriorate_speed = 10  # Lower is slower
        self.led_color_add = True
        self.brightness = start_brightness
        self.min_brightness = min_brightness
        self.stellar.set_brightness(self.brightness)
        self.last_update = time.ticks_ms()

        for x in range(self.uni_width):
            row = []
            for y in range(self.uni_height):
                led = Led(x, y, vopak_logo[x][y])
                self.leds.append(led)
                row.append(led)
            self.leds_map.append(row)

    # Changes the speed of handling updates, in effect changing the speed with which worms move
    def change_speed(self, adjustment):
        if self.fps - adjustment > 10:
            self.fps -= adjustment
        elif self.fps + adjustment < self.max_fps:
            self.fps += adjustment
        self.tfps = 1000 // self.fps

    @micropython.native
    def set_led_color(self, x, y, color, ignore_add=False):
        if self.led_color_add and not ignore_add:
            led = self.leds_map[x][y]
            new_color = []
            for i in range(3):
                added = led.color[i] + color[i]
                new_color.append(min(added, 255))
            self.leds_map[x][y].color = new_color
        else:
            self.leds_map[x][y].color = color

    # Slower with viper
    def update_leds(self):
        for led in self.leds:
            # Update the color in the LED object
            led.color[0] = max(led.color[0] - self.deteriorate_speed, vopak_logo[led.x][led.y][0])
            led.color[1] = max(led.color[1] - self.deteriorate_speed, vopak_logo[led.x][led.y][1])
            led.color[2] = max(led.color[2] - self.deteriorate_speed, vopak_logo[led.x][led.y][2])

            # Update the color on the screen
            self.graphics.set_pen(self.graphics.create_pen(*led.color))
            self.graphics.pixel(led.x, led.y)
        self.stellar.update(self.graphics)

    def black_out(self):
        for led in self.leds:
            led.color = (0, 0, 0)
            self.update_leds()

    def wait_for_loop(self):
        # Wait for the next frame
        diff = time.ticks_diff(self.last_update, time.ticks_ms())
        if diff < self.tfps:
            time.sleep_ms(self.tfps - diff)
        self.last_update = time.ticks_ms()

    def change_brightness(self, param):
        self.brightness += param
        if self.brightness >= 1.0:
            self.brightness = 1.0
        elif self.brightness <= self.min_brightness:
            self.brightness = self.min_brightness
        self.stellar.set_brightness(self.brightness)
