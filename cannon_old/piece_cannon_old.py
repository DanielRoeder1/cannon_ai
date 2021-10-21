import pygame
from cannon.constants import BOARD_CELL_SIZE, TOKEN_CLR_OUTLINE

class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.x = 0
        self.y = 0
        self.table_to_coord()
        self.PADDING = 10
        self.OUTLINE = 2

    def table_to_coord(self):
        self.x = BOARD_CELL_SIZE[0] * self.col + BOARD_CELL_SIZE[0]
        self.y = BOARD_CELL_SIZE[1] * self.row + BOARD_CELL_SIZE[1]

    def draw(self, win):
        radius = BOARD_CELL_SIZE[0] // 2 - self.PADDING
        pygame.draw.circle(win, TOKEN_CLR_OUTLINE, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)

    def move(self, row, col):
        self.row = row
        self.col = col
        self.table_to_coord()
