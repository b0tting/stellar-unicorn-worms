import random
import time

import picounicorn

picounicorn.init()


class Led:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GREY = (70, 70, 70)
    COLORS = [RED, GREEN, BLUE]

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color


class UnicornLeds:
    def __init__(self, w, h):
        self.speed = 10  # Lower is slower
        self.uni_width = w
        self.uni_height = h
        self.leds = []
        self.leds_map = []
        self.deteriorate_speed = 16  # Lower is slower
        self.led_color_add = True
        for x in range(w):
            row = []
            for y in range(h):
                led = Led(x, y, (0, 0, 0))
                self.leds.append(led)
                row.append(led)
            self.leds_map.append(row)

    # Changes the speed of handling updates, in effect changing the speed with which worms move
    def change_speed(self, adjustment):
        self.speed = max(self.speed - adjustment, 1)

    def set_led_color(self, x, y, color):
        if self.led_color_add:
            led = self.leds_map[x][y]
            new_color = []
            for i in range(3):
                added = led.color[i] + color[i]
                new_color.append(min(added, 255))
            self.leds_map[x][y].color = new_color
        else:
            self.leds_map[x][y].color = color

    def deteriorate(self):
        for led in self.leds:
            r, g, b = [max(color - self.deteriorate_speed, 0) for color in led.color]
            led.color = (r, g, b)

    def update_leds(self):
        for led in self.leds:
            picounicorn.set_pixel(led.x, led.y, *led.color)

    def wait_for_loop(self):
        time.sleep(1 / self.speed)


class Worm:
    def __init__(self, leds: UnicornLeds, worm_color, body_color):
        self.led_manager = leds
        self.x = random.randint(0, unicorn_leds.uni_width - 2)
        self.x_speed = 1
        self.y = random.randint(0, unicorn_leds.uni_height - 1)
        self.y_speed = 0
        self.turn_chance = 0.2
        self.worm_color = worm_color
        self.body_color = body_color

    def move(self):
        # We drop a body in the location we just left
        self.draw_body()

        self.x = self.x + self.x_speed
        self.y = self.y + self.y_speed

        # Consider turning - this will not move us, only point the worm in another direction
        if touching := self.is_touching_edge():
            self.turn(touching)
        elif random.random() < self.turn_chance:
            self.turn()

        self.draw_head()

    def draw_body(self):
        self.led_manager.set_led_color(self.x, self.y, self.body_color)

    def draw_head(self):
        self.led_manager.set_led_color(self.x, self.y, self.worm_color)

    def is_touching_edge(self):
        return (
            self.x == 0
            or self.x >= self.led_manager.uni_width - 1
            or self.y == 0
            or self.y >= self.led_manager.uni_height - 1
        )

    def turn(self, touching_edge=False):
        if self.x_speed != 0:
            self.x_speed = 0
            if self.y <= 0:
                self.y_speed = 1
            elif touching_edge:
                self.y_speed = -1
            else:
                self.y_speed = 1 if random.random() > 0.5 else -1
        elif self.y_speed != 0:
            self.y_speed = 0
            if self.x <= 0:
                self.x_speed = 1
            elif touching_edge:
                self.x_speed = -1
            else:
                self.x_speed = 1 if random.random() > 0.5 else -1


class ButtonPresses:
    def __init__(self):
        self.button_map = {
            picounicorn.BUTTON_A: False,
            picounicorn.BUTTON_B: False,
            picounicorn.BUTTON_X: False,
            picounicorn.BUTTON_Y: False,
        }

    def is_pressed(self, uni_button):
        result = False
        if picounicorn.is_pressed(uni_button) and not self.button_map[uni_button]:
            self.button_map[uni_button] = True
            result = True
        elif not picounicorn.is_pressed(uni_button):
            self.button_map[uni_button] = False
        return result

    def handle_buttons(self):
        # Button A adds a new worm
        if self.is_pressed(picounicorn.BUTTON_A):
            new_color = random.choice(Led.COLORS)
            worms.append(Worm(unicorn_leds, new_color, Led.GREY))
        # Button B deletes the last added worm
        if self.is_pressed(picounicorn.BUTTON_B):
            if len(worms) > 0:
                worms.pop()
        # Button X slows everything down
        if self.is_pressed(picounicorn.BUTTON_X):
            unicorn_leds.change_speed(2)
        # And finally, button y speeds it up again
        if self.is_pressed(picounicorn.BUTTON_Y):
            unicorn_leds.change_speed(-2)


# Unicorn leds managed a matrix of virtual leds and manages the merging
# of colors. Changes are made there, before calling the update method that
# actually updates the screen.
unicorn_leds = UnicornLeds(picounicorn.get_width(), picounicorn.get_height())

worms = [
    Worm(unicorn_leds, Led.RED, Led.GREY),
    Worm(unicorn_leds, Led.GREEN, Led.GREY),
    Worm(unicorn_leds, Led.BLUE, Led.GREY),
]
buttons = ButtonPresses()
while True:
    buttons.handle_buttons()
    for worm in worms:
        # This moves the worm and tells unicorn_leds what to light up
        worm.move()

    # Here we darken all leds a little
    unicorn_leds.deteriorate()

    # And this function finally lights the leds
    unicorn_leds.update_leds()

    unicorn_leds.wait_for_loop()
