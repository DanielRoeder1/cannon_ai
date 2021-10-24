import pygame
from cannon.board import Board
from cannon.constants import P1_CLR, P2_CLR, BOARD_CELL_SIZE

class Game:
    def __init__(self, win):
        self._init()
        self.win = win
        self.towns_placed = 0

    def update(self):
        self.board.draw_all(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = 1
        # Init with P1 town positions
        self.valid_moves = {(0, 0), (0, 1), (0, 2),(0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0,9)}



    def select(self, row, col):
        # TODO This might lead to pieces not being able to do anything when they reach the last row: But are they allowed ot do anything?
        if self.towns_placed == 2 and -1 < row < 10:
            if self.selected and (row,col) in self.valid_moves:
                self.move(row, col, self.valid_moves.get((row,col)))
            else:
                piece = self.board.get_piece((row, col))
                if piece != 0 and piece == self.turn:
                    self.selected = (row,col)
                    self.valid_moves, cannon_found = self.board.get_valid_moves(row,col)
        elif self.towns_placed < 2:
            self.place_town(row,col)
        self.board.get_all_moves(self.turn)

    # TODO: Towns are considered when looking for cannon formations
    def place_town(self, row,col):
        if (row,col) in self.valid_moves:
            self.board.board_state[row][col] = self.towns_placed+1
            self.board.town_pos[(row,col)] = self.towns_placed+1
            self.board.town_pos_list[self.towns_placed] = [row,col,self.towns_placed+1]
            self.turn = 2
            self.valid_moves = {(9, 0), (9, 1), (9, 2),(9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (9,9)}
            self.towns_placed+=1
        # Let the game begin with P1 starting
        if self.towns_placed == 2:
            self.turn = 1
            self.valid_moves = {}

    def move(self, row, col, target_value):
        #print(self.valid_moves)
        if target_value == 0:
            self.board.board_state[row][col] = 0
            #if (row,col) in self.board.town_pos:
            #    print("The winner is: "+str(self.turn))
        else:
            self.board.move(target_value, row, col)
        self.change_turn()

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, (0,0,255),
                               (col * BOARD_CELL_SIZE[0] + BOARD_CELL_SIZE[0] , row * BOARD_CELL_SIZE[0] + BOARD_CELL_SIZE[0]  ), 15)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == 1:
            self.turn = 2
        else:
            self.turn = 1

    def ai_move(self, board):
        self.board.board_state = board
        self.change_turn()
