from cannon.constants import WINDOW_HEIGHT, WINDOW_WIDTH, BOARD_CELL_SIZE
from cannon.game import Game
import pygame
from AlphaBeta.algorithm import AlphaBeta

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

        if game.turn == 1 and game.towns_placed == 2:
            algorithm = AlphaBeta(game.board)
            #value, new_board = algorithm.minimax(3,True,())
            #value, new_board = algorithm.alphabeta(4,float("-inf"), float("inf"),1)
            value, new_board = algorithm.alphabeta_TT(4,float("-inf"), float("inf"),1, algorithm.TT.z_key)

            game.move(new_board[0][0], new_board[0][1], new_board[1])

            game.turn =2
            print("##########")
            print(f"Score: {value}")
            print(f"Num of Evals: {algorithm.counter}")
            print(f"Move: {new_board}")
            print("##########")
            #game.ai_move(new_board)



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
