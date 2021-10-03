from cannon.constants import WINDOW_HEIGHT, WINDOW_WIDTH, BOARD_CELL_SIZE
from cannon.game import Game
import pygame

window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Check if the user clicked close to a gridpoint
def mouse_to_table(pos):
    x,y = pos
    allowed_shift = 35
    if dist_to_grid_point(x) < allowed_shift and dist_to_grid_point(y) < allowed_shift:
        col = round((x / BOARD_CELL_SIZE[0])) -1
        row = round((y / BOARD_CELL_SIZE[0])) -1
        if col in range(0,10) and row in range(0,10):
            return row,col
        else:
            return False


def dist_to_grid_point(coord):
    tmp_num = (coord % BOARD_CELL_SIZE[0])
    if tmp_num > (BOARD_CELL_SIZE[0] / 2):
        shift_to_gridpoint = BOARD_CELL_SIZE[0] - tmp_num
    else:
        shift_to_gridpoint = tmp_num

    return shift_to_gridpoint



def main_loop():
    run = True
    clock = pygame.time.Clock()
    game = Game(window)

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                loc = mouse_to_table(pos)
                if loc:
                    game.select(loc[0], loc[1])


        game.update()
        pygame.display.update()

    pygame.quit()


main_loop()
