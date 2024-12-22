import random
import sys

from math import ceil

import micropython

from worms.led import Led
from worms.unicorn_leds import UnicornLeds

class Worm:
    EDGE_LEFT = 1
    EDGE_RIGHT = 2
    EDGE_TOP = 3
    EDGE_BOTTOM = 4
    MAX_AGE = 5000
    DYING_BOUNDARY = 1000
    AGE_SLOWDOWN = 6
    DEFAULT_SPEED = 1

    def __init__(self, leds: UnicornLeds, worms=None, height_adjust=1):
        self.led_manager = leds
        self.x = random.randint(0, leds.uni_width - 2)
        self.x_speed = self.DEFAULT_SPEED
        self.y = random.randint(height_adjust, leds.uni_height - 1)
        self.y_speed = 0
        self.turn_chance = 0.25
        self.worm_color = Led.BLUE
        self.age = 0
        self.wait_move = 0
        self.worms = worms if worms else []
        self.height_adjust = height_adjust
        self.init_worm()

    def init_worm(self):
        pass

    @micropython.native
    def wait_for_age(self):
        if self.is_dying():
            if self.wait_move == 0:
                inverted_life_left = self.DYING_BOUNDARY - self.life_left()
                quartile = (
                    ceil((inverted_life_left * self.AGE_SLOWDOWN) / self.DYING_BOUNDARY)
                    + 1
                )
                self.wait_move = quartile

            if self.wait_move > 0:
                self.wait_move -= 1

        return self.wait_move > 0

    @micropython.native
    def move(self):
        # Dying worms move slower

        if not self.wait_for_age():
            self.x = self.x + self.x_speed
            self.y = self.y + self.y_speed

        # Consider turning - this will not move us, only point the worm in another direction
        if self.is_ramming_edge() or self.want_to_turn():
            self.turn()
        self.draw_head(self.get_worm_color())
        if self.age < sys.maxsize - 1:
            self.age += 1

    def get_worm_color(self):
        life_left = self.life_left()
        if life_left < self.DYING_BOUNDARY:
            return self.age_worm_color(self.worm_color)
        else:
            return self.worm_color

    @micropython.native
    def age_worm_color(self, color):
        new_color = []
        average = sum(color) / len(color)
        invert_life_left = self.DYING_BOUNDARY - self.life_left()

        # Calculate how much to add or substract from each color to
        # make the worm appear to fade out
        fraction = round((average * invert_life_left) / self.DYING_BOUNDARY)
        for i in range(3):
            current_color = color[i]
            if current_color > average:
                # First go to grey. Fade the primary color down
                current_color = max(current_color - (2 * fraction), average)
            else:
                # And fade the secondary colors up
                current_color = min(current_color + fraction, average)
            # Finally, fade the entire color down
            new_color.append(round(max(current_color - fraction, 0)))
        return new_color

    def draw_head(self, color):
        try:
            self.led_manager.set_led_color(self.x, self.y, color)
        except IndexError:
            raise Exception(
                f"{__class__.__name__} out of bounds with X {self.x}, speed {self.x_speed}, Y {self.y}, speed {self.y_speed}"
            )

    @micropython.native
    def is_touching_edge(self, edge):
        is_touching = False
        if edge == self.EDGE_LEFT:
            is_touching = self.x == 0
        elif edge == self.EDGE_RIGHT:
            is_touching = self.x >= self.led_manager.uni_width - 1
        elif edge == self.EDGE_BOTTOM:
            is_touching = self.y == self.height_adjust
        elif edge == self.EDGE_TOP:
            is_touching = self.y >= self.led_manager.uni_height - 1
        return is_touching

    @micropython.native
    def is_touching_any_edge(self):
        is_touching = False
        for is_touching_now in [
            self.EDGE_LEFT,
            self.EDGE_TOP,
            self.EDGE_RIGHT,
            self.EDGE_BOTTOM,
        ]:
            is_touching = is_touching or self.is_touching_edge(is_touching_now)
        return is_touching

    @micropython.native
    def is_ramming_edge(self):
        return (
            (self.is_touching_edge(self.EDGE_LEFT) and self.x_speed < 0)
            or (self.is_touching_edge(self.EDGE_RIGHT) and self.x_speed > 0)
            or (self.is_touching_edge(self.EDGE_BOTTOM) and self.y_speed < 0)
            or (self.is_touching_edge(self.EDGE_TOP) and self.y_speed > 0)
        )

    @micropython.native
    def turn(self):
        if self.x_speed != 0:
            self.x_speed = 0
            if self.is_touching_edge(self.EDGE_BOTTOM):
                self.y_speed = self.DEFAULT_SPEED
            elif self.is_touching_edge(self.EDGE_TOP):
                self.y_speed = -self.DEFAULT_SPEED
            else:
                self.y_speed = self.decide_up_or_down()
        elif self.y_speed != 0:
            self.y_speed = 0
            if self.is_touching_edge(self.EDGE_LEFT):
                self.x_speed = self.DEFAULT_SPEED
            elif self.is_touching_edge(self.EDGE_RIGHT):
                self.x_speed = -self.DEFAULT_SPEED
            else:
                self.x_speed = self.decide_left_or_right()

    def die(self):
        self.age = self.MAX_AGE

    def is_dead(self):
        return self.life_left() <= 0

    def life_left(self):
        return self.MAX_AGE - self.age

    def is_dying(self):
        return self.life_left() < self.DYING_BOUNDARY

    def want_to_turn(self):
        return random.random() < self.turn_chance

    def decide_up_or_down(self):
        return 1 if random.random() > 0.5 else -1

    def decide_left_or_right(self):
        return 1 if random.random() > 0.5 else -1


class TurnyWorm(Worm):
    def init_worm(self):
        self.turn_chance = 0.6
        self.worm_color = Led.RED


class StraightWorm(Worm):
    def init_worm(self):
        self.turn_chance = 0.2
        self.worm_color = Led.BLUE


class WallWorm(Worm):
    def init_worm(self):
        self.small_turn_chance = 0.1
        self.turn_chance = 0.6
        self.worm_color = Led.GREEN

    def want_to_turn(self):
        if self.is_touching_any_edge():
            return random.random() < self.small_turn_chance
        else:
            return random.random() < self.turn_chance


class RainbowWorm(Worm):
    RAINBOW_COLORS = [Led.RED, Led.ORANGE, Led.YELLOW, Led.GREEN, Led.BLUE, Led.PURPLE]

    def init_worm(self):
        self.turn_chance = 0.3
        self.rainbow_index = 0

    def get_worm_color(self):
        color = self.RAINBOW_COLORS[self.rainbow_index]
        color = [max(rgb - 50, 0) for rgb in color]
        self.rainbow_index += 1
        self.rainbow_index %= len(self.RAINBOW_COLORS)
        color = self.age_worm_color(color)
        return color


class SlowWorm(Worm):
    def init_worm(self):
        self.turn_chance = 0.6
        self.worm_color = Led.PURPLE
        self.move_this_turn = True

    @micropython.native
    def move(self):
        if self.move_this_turn:
            self.move_this_turn = False
            super(SlowWorm, self).move()
        else:
            self.move_this_turn = True
            self.draw_head(self.get_worm_color())


class RedHeadWorm(Worm):
    # This worm always turns the same way and has a red head
    def init_worm(self):
        self.worm_body_color = Led.GREY
        self.worm_color = Led.RED
        self.last_x = self.x
        self.last_y = self.y

    def move(self):
        # This worm jots down it's last position. We have the superclass draw our new led,
        # then we draw a grey led in our old position
        self.last_x = self.x
        self.last_y = self.y
        super(RedHeadWorm, self).move()
        self.led_manager.set_led_color(
            self.last_x, self.last_y, list(self.worm_body_color), ignore_add=True
        )

    def decide_up_or_down(self):
        return 1

    def decide_left_or_right(self):
        return 1


class ChasingWorm(Worm):
    def init_worm(self):
        self.worm_color = Led.GREEN
        self.worm_second_color = Led.RED

    def move(self):
        super().move()
        # This worm tries to find another worm and chase that
        closest_worm = None
        for worm in self.worms:
            if worm != self:
                # Find the closest worm
                if not closest_worm or self.distance_to(worm) < self.distance_to(
                    closest_worm
                ):
                    closest_worm = worm

        # Only chase if further away than 2 spaces
        if closest_worm:
            if closest_worm.x > (self.x + 2):
                self.x_speed = self.DEFAULT_SPEED
                self.y_speed = 0
            elif closest_worm.x < (self.x - 2):
                self.x_speed = -self.DEFAULT_SPEED
                self.y_speed = 0
            elif closest_worm.y > (self.y + 2):
                self.y_speed = self.DEFAULT_SPEED
                self.x_speed = 0
            elif closest_worm.y < (self.y - 2):
                self.y_speed = -self.DEFAULT_SPEED
                self.x_speed = 0

    def distance_to(self, worm):
        return abs(self.x - worm.x) + abs(self.y - worm.y)

    def get_worm_color(self):
        color = self.worm_second_color if self.age % 2 == 0 else self.worm_color
        color = self.age_worm_color(color)
        return color


class ScaredWorm(Worm):
    def init_worm(self):
        self.scare_factor = 2
        self.worm_color = Led.GREY
        self.worm_second_color = Led.WHITE

    def move(self):
        super().move()
        # This worm tries to find another worm and chase that
        if not self.is_touching_any_edge():
            closest_worm = None
            for worm in self.worms:
                if worm != self:
                    # Find the closest worm
                    if not closest_worm or self.distance_to(worm) < self.distance_to(
                        closest_worm
                    ):
                        closest_worm = worm

            # Only chase if further away than 2 spaces
            if closest_worm:
                if self.x <= closest_worm.x <= (self.x + self.scare_factor):
                    self.x_speed = -self.DEFAULT_SPEED
                    self.y_speed = 0
                elif self.x >= closest_worm.x >= (self.x - self.scare_factor):
                    self.x_speed = self.DEFAULT_SPEED
                    self.y_speed = 0

                if self.y <= closest_worm.y <= (self.y + self.scare_factor):
                    self.y_speed = -self.DEFAULT_SPEED
                    self.x_speed = 0
                elif self.y >= closest_worm.y >= (self.y - self.scare_factor):
                    self.y_speed = self.DEFAULT_SPEED
                    self.x_speed = 0

    def distance_to(self, worm):
        return abs(self.x - worm.x) + abs(self.y - worm.y)

    def get_worm_color(self):
        color = self.worm_second_color if self.age % 2 == 0 else self.worm_color
        color = self.age_worm_color(color)
        return color

worm_collection = [
    ChasingWorm,
    ScaredWorm,
    TurnyWorm,
    StraightWorm,
    WallWorm,
    SlowWorm,
    RainbowWorm,
    RedHeadWorm,
]
