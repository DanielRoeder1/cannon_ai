import pygame
from cannon.board import Board
from cannon.constants import P1_CLR, P2_CLR, BOARD_CELL_SIZE

class Game:
    def __init__(self, win):
        self._init()
        self.win = win

    def update(self):
        self.board.draw_all(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = P1_CLR
        self.valid_moves = {}

    def select(self, row, col):
        if self.selected and (row,col) in self.valid_moves:
            self._move(row, col, self.valid_moves.get((row,col)))
        else:
            piece = self.board.get_piece(row, col)
            if piece != 0 and piece.color == self.turn:
                self.selected = piece
                self.valid_moves = self.board.get_valid_moves(piece)


    def _move(self, row, col, target_value):
        if target_value == 0:
            self.board.board_state[row][col] = 0
        else:
            move_piece = self.board.get_piece(target_value[0], target_value[1])
            self.board.move(move_piece, row, col)
        self.change_turn()
        print(self.board.p1_left)
        print(self.board.p2_left)


    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, (0,0,255),
                               (col * BOARD_CELL_SIZE[0] + BOARD_CELL_SIZE[0] , row * BOARD_CELL_SIZE[0] + BOARD_CELL_SIZE[0]  ), 15)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == P1_CLR:
            self.turn = P2_CLR
        else:
            self.turn = P1_CLR