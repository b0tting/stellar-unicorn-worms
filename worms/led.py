class Led:
    RED = (255, 50, 50)
    GREEN = (50, 255, 50)
    WHITE = (250, 250, 250)
    BLUE = (50, 50, 255)
    YELLOW = (255, 255, 50)
    PURPLE = (255, 50, 255)
    ORANGE = (255, 120, 50)
    GREY = (150, 150, 150)

    COMMON_COLORS = [RED, GREEN, WHITE, BLUE, YELLOW, PURPLE, ORANGE, GREY]

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
