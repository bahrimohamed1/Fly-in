import pygame  # pyright: ignore[reportMissingImports]


WIDTH = 900
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("TEST")

RED = (255, 0, 0)  # barriar
GREEN = (0, 255, 0)  # start
BLUE = (0, 0, 255) # opened
YELLOW = (255, 255, 0)  # end
WHITE = (255, 255, 255)  # default
BLACK = (0, 0, 0)  # closed
PURPLE = (127, 0, 255) # path


class zone:
    def __init__(self, y: int, x: int, width: int):
        self.width = width
        self.y = y
        self.x = x
        self.color = WHITE

    def get_pos(self):
        return self.y, self.x

    def is_closed(self):
        return self.color == BLACK

    def is_opened(self):
        return self.color == BLUE

    def is_barriar(self):
        return self.color == RED

    def is_start(self):
        return self.color == GREEN

    def is_end(self):
        return self.color == YELLOW
        
    def reset(self):
        self.color = WHITE
        
    def set_closed(self):
        self.color = BLACK

    def set_opened(self):
        self.color = BLUE

    def set_barriar(self):
        self.color = RED

    def set_start(self):
        self.color = GREEN

    def set_end(self):
        self.color = YELLOW
        
    def set_path(self):
        self.color = PURPLE
        
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

