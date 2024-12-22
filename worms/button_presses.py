import machine

class ButtonPresses:
    def __init__(self, stellar_unicorn, unicorn_leds, life_and_death):
        self.stellar_unicorn = stellar_unicorn
        self.button_map = {
            stellar_unicorn.SWITCH_A: False,
            stellar_unicorn.SWITCH_B: False,
            stellar_unicorn.SWITCH_C: False,
            stellar_unicorn.SWITCH_D: False,
        }
        self.life_and_death = life_and_death
        self.unicorn_leds = unicorn_leds

    def is_pressed(self, uni_button):
        result = False
        if (
            self.stellar_unicorn.is_pressed(uni_button)
            and not self.button_map[uni_button]
        ):
            self.button_map[uni_button] = True
            result = True
        elif not self.stellar_unicorn.is_pressed(uni_button):
            self.button_map[uni_button] = False
        return result

    @micropython.native
    def handle_buttons(self):
        # Button A adds a new worm
        if self.is_pressed(self.stellar_unicorn.SWITCH_A):
            self.life_and_death.procreate(always=True)
        # Button B deletes the last added worm
        if self.is_pressed(self.stellar_unicorn.SWITCH_B):
            self.life_and_death.shoot_worm()
        # Button X slows everything down
        if self.is_pressed(self.stellar_unicorn.SWITCH_C):
            self.unicorn_leds.change_speed(+10)
        # And finally, button y speeds it up again
        if self.is_pressed(self.stellar_unicorn.SWITCH_D):
            self.unicorn_leds.change_speed(-10)

        if self.is_pressed(self.stellar_unicorn.SWITCH_BRIGHTNESS_UP):
            self.unicorn_leds.change_brightness(0.1)
        if self.is_pressed(self.stellar_unicorn.SWITCH_BRIGHTNESS_DOWN):
            self.unicorn_leds.change_brightness(-0.1)
        if self.is_pressed(self.stellar_unicorn.SWITCH_SLEEP):
            machine.reset()
