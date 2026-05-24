import pygame


WIDTH = 900
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("TEST")

RED = (255, 0, 0)  # barriar
GREEN = (0, 255, 0)  # start
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)  # end
WHITE = (255, 255, 255)  # opened
BLACK = (0, 0, 0)  # closed


class zone:
    def __init__(self, y: int, x: int):
        self.y = y
        self.x = x
        self.color = WHITE

    def get_pos(self):
        return self.y, self.x

    def is_closed(self):
        return self.color == BLACK

    def is_open(self):
        return self.color == WHITE

    def is_barriar(self):
        return self.color == RED

    def is_start(self):
        return self.color == GREEN

    def is_end(self):
        self.color == YELLOW
