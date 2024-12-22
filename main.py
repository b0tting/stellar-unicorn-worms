import gc

from stellar import StellarUnicorn
from picographics import PicoGraphics, DISPLAY_STELLAR_UNICORN as DISPLAY

from worms.worms import worm_collection
from worms.unicorn_leds import UnicornLeds
from worms.button_presses import ButtonPresses
from worms.life_and_death import LifeAndDeath
MIN_BRIGHTNESS = 0.2

# these two are the modules already set up by Pimoroni
stellar = StellarUnicorn()
graphics = PicoGraphics(DISPLAY)

# Unicorn leds managed a matrix of virtual leds and manages the merging
# of colors. Changes are made there, before calling the update method that
# actually updates the screen.
unicorn_leds = UnicornLeds(graphics, stellar, min_brightness=MIN_BRIGHTNESS)

# Life and death manages the worms and their procreation
life_and_death = LifeAndDeath(worm_collection, unicorn_leds)

buttons = ButtonPresses(stellar, unicorn_leds, life_and_death)
while True:
    buttons.handle_buttons()
    life_and_death.handle_life_and_death()

    # And this function finally sends the new worms information to the screen
    unicorn_leds.update_leds()

    # This is the main loop, it waits for the next frame
    unicorn_leds.wait_for_loop()

    # gc.collect()
