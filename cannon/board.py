from cannon.constants import BOARD_COLS, BOARD_ROWS, BOARD_CLR_dark, BOARD_CLR_light, BOARD_CELL_SIZE, P1_CLR, P2_CLR, BOARD_CLR_BORDER, WINDOW_WIDTH, WINDOW_HEIGHT
import pygame
from cannon.piece import Piece

class Board:
    def __init__(self):
        self.board_state = []
        self.p1_left = 15
        self.p2_left = 15
        self.init_board()


    # Initialise pieces on the board
    def init_board(self):
        for row in range(BOARD_ROWS):
            self.board_state.append([])
            for col in range(BOARD_COLS):
                if row in range(1,4) and col % 2 != 0:
                    self.board_state[row].append(Piece(row, col, P1_CLR))
                elif row in range(6,9) and col % 2 == 0:
                    self.board_state[row].append(Piece(row, col, P2_CLR))
                else:
                    self.board_state[row].append(0)


    # Draw the chess like board including border
    def draw_board(self, win):
        win.fill(BOARD_CLR_BORDER)
        pygame.draw.rect(win, BOARD_CLR_dark,(BOARD_CELL_SIZE[0], BOARD_CELL_SIZE[1], WINDOW_WIDTH - BOARD_CELL_SIZE[0] *2 , WINDOW_HEIGHT -BOARD_CELL_SIZE[1] *2))
        for row in range(BOARD_ROWS -1):
            for col in range(row % 2,BOARD_COLS -1,2):
                    pygame.draw.rect(win, BOARD_CLR_light, (row * BOARD_CELL_SIZE[1] + BOARD_CELL_SIZE[0], col * BOARD_CELL_SIZE[0] + BOARD_CELL_SIZE[1], BOARD_CELL_SIZE[0], BOARD_CELL_SIZE[1]) )


    def draw_all(self, win):
        self.draw_board(win)
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board_state[row][col]
                if piece != 0:
                    piece.draw(win)
                    pass


    # Change state representation with move
    def move(self, piece, row, col):
        self.board_state[piece.row][piece.col], self.board_state[row][col] = self.board_state[row][col], self.board_state[piece.row][piece.col]
        piece.move(row, col)


    def get_valid_moves(self, piece):
        valid_moves = {}
        valid_moves.update(self.check_soldier_move(piece))

        return valid_moves


    def check_soldier_move(self, piece):
        if piece.color == P1_CLR:
            direction_mod = 1
        else:
            direction_mod = -1

        # create three frontal postitions for basic move
        front_row = piece.row +direction_mod
        if  front_row <= BOARD_ROWS-1 and  front_row >= 0:
            frontal_positions = [(front_row, piece.col + i) for i in [-1,0,1] if piece.col+i <= BOARD_ROWS-1 and piece.col+i >= 0]

        else: frontal_positions = []
        side_positions = [(piece.row, piece.col+i) for i in [-1,1] if piece.col+i <= BOARD_ROWS-1 and piece.col+i >= 0]
        side_positions.extend(frontal_positions)

        moves = {}
        adj_friendly_pos = []
        allow_retreat = False

        # Check front and side positions -> if we find a friendly look for cannon
        for pos in side_positions:
            adj_piece = self.board_state[pos[0]][pos[1]]
            if adj_piece != 0:
                if adj_piece.color != piece.color:
                    moves[pos] = (piece.row, piece.col)
                    allow_retreat = True
                else:
                    # Found a friendly in front or side positions -> see if we can combine this to a cannon
                    adj_friendly_pos.append(pos)
                    moves.update(self.search_cannon2(piece,pos))

            # Not allowed to set non sitewards move when field is empty
            elif pos[0] != piece.row:
                moves[pos] = (piece.row, piece.col)

        # Checking the back only needed for checking retreats
        if not allow_retreat:
            back_row = piece.row - direction_mod
            if back_row <= BOARD_ROWS - 1 and back_row >= 0:
                back_positions = [(back_row, piece.col + i) for i in [-1, 0, 1] if piece.col + i <= BOARD_ROWS - 1 and piece.col + i >= 0]

            for pos in back_positions:
                adj_piece = self.board_state[pos[0]][pos[1]]
                if adj_piece != 0 and adj_piece.color != piece.color:
                        allow_retreat = True

        if allow_retreat:
            moves.update(self.check_soldier_retreat(piece, direction_mod))

        return moves


    def search_cannon2(self, piece, pos):
        moves = {}
        opposite_dir_vec = self.substract_tuples((piece.row,piece.col), pos)
        opposite_pos = self.add_tuples((piece.row,piece.col), opposite_dir_vec)

        if self.check_boundary(opposite_pos):
            adj_piece = self.board_state[opposite_pos[0]][opposite_pos[1]]
            if adj_piece != 0 and adj_piece.color == piece.color:
                # Found three piece row
                look_ahead_back = self.add_tuples(opposite_pos, opposite_dir_vec)
                look_ahead_front =  self.substract_tuples(pos, opposite_dir_vec)

                if self.check_boundary(look_ahead_front) and self.board_state[look_ahead_front[0]][look_ahead_front[1]] == 0:
                    # only checking for move so if the field is empty
                    # if I also want to check for cannon formation check ahead_piece.color != piece.color
                    # slide move front
                    moves[look_ahead_front] = opposite_pos
                    look_ahead_front_further = self.substract_tuples(look_ahead_front, opposite_dir_vec)
                    if self.check_boundary(look_ahead_front_further):
                        p = self.board_state[look_ahead_front_further[0]][look_ahead_front_further[1]]
                        if p!=0 and p.color != piece.color:
                            moves[look_ahead_front_further] = 0

                if self.check_boundary(look_ahead_back) and self.board_state[look_ahead_back[0]][look_ahead_back[1]] == 0:
                    # only checking for move so if the field is empty
                    # if I also want to check for cannon formation check ahead_piece.color != piece.color
                    # slide move back
                    moves[look_ahead_back] = pos
                    look_ahead_back_further = self.add_tuples(look_ahead_back, opposite_dir_vec)
                    if self.check_boundary(look_ahead_back_further):
                        p = self.board_state[look_ahead_back_further[0]][look_ahead_back_further[1]]
                        if p != 0 and p.color != piece.color:
                            moves[look_ahead_back_further] = 0
        print(moves)
        return moves


    def check_soldier_retreat(self, piece, direction_mod):
        moves = {}
        if piece.row + (direction_mod * -2) <= BOARD_ROWS-1 and  piece.row +(direction_mod *-2)>= 0:
            retreat_positions = [(piece.row + (direction_mod *-2), piece.col + i) for i in [-2,0,2] if piece.col+i <= BOARD_ROWS-1 and piece.col+i >= 0]
        else:
            return {}

        for pos in retreat_positions:
            if self.board_state[pos[0]][pos[1]] == 0:
                if self.board_state[self.mean(piece.row, pos[0])][self.mean(piece.col, pos[1])] == 0:
                    moves[pos] = (piece.row,piece.col)
            else:
                continue

        return moves


    def check_boundary(self, pos):
        if 0 <= pos[0] <= BOARD_ROWS - 1 and 0 <= pos[1] <= BOARD_ROWS - 1:
            return True
        else:
            return False
    def add_tuples(self,tup1,tup2):
        return(tup1[0] + tup2[0], tup1[1] + tup2[1])
    def substract_tuples(self,tup1,tup2):
        return(tup1[0] - tup2[0], tup1[1] - tup2[1])
    def mean(self,num1, num2):
        return (num1 + num2) //2
    def get_piece(self, row, col):
        return self.board_state[row][col]

    # TODO remove function is not called so p1.left is not updated
    def remove(self, piece):
        self.board_state[piece.row][piece.col] = 0
        if piece.color == P1_CLR:
            self.p1_left -= 1
        else:
            self.p2_left -= 1






