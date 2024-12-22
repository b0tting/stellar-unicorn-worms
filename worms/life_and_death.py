import random
from worms.worms import Worm


class LifeAndDeath:
    def __init__(
        self,
        worm_collection,
        unicorn_leds,
        min_worms_count=2,
    ):
        self.min_worms_count = min_worms_count
        self.worms = []
        self.worm_collection = worm_collection
        self.unicorn_leds = unicorn_leds

    def get_random_worm(self):
        return random.choice(self.worm_collection)(self.unicorn_leds, self.worms)

    @micropython.native
    def handle_life_and_death(self):
        for worm in self.worms:
            worm.move()
            if worm.is_dead():
                self.worms.remove(worm)
        self.procreate()

    def shoot_worm(self):
        if len(self.worms) > 0:
            self.worms.pop()

    # Todo: Worms should have control over procreation themselves
    @micropython.native
    def procreate(self, always=False):
        # Depending on the number of worms, we might not want to procreate
        birth = True
        birth_range = range(0, len(self.worms) - self.min_worms_count + 1)
        for _ in birth_range:
            birth = birth and random.randint(0, Worm.MAX_AGE) == 1

        if birth or always:
            self.worms.append(self.get_random_worm())
