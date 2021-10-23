from cannon.constants import BOARD_COLS, BOARD_ROWS, BOARD_CLR_dark, BOARD_CLR_light, BOARD_CELL_SIZE, P1_CLR, P2_CLR, BOARD_CLR_BORDER, WINDOW_WIDTH, WINDOW_HEIGHT, TOKEN_CLR_OUTLINE
import pygame
import numpy as np

class Board:
    def __init__(self):
        self.board_state = []
        self.p1_left = 15
        self.p2_left = 15
        self.init_board()
        self.town_pos = {}
        self.turn = 0

        #Evals
        self.soldier_capture = 0
        self.cannon_capture = 0


    # Initialise pieces on the board
    def init_board(self):
        for row in range(BOARD_ROWS):
            self.board_state.append([])
            for col in range(BOARD_COLS):
                if row in range(1,4) and col % 2 != 0:
                    self.board_state[row].append(1)
                elif row in range(6,9) and col % 2 == 0:
                    self.board_state[row].append(2)
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
                self.draw_piece(win,row,col, piece)

    def draw_piece(self, win, row ,col, id):
        OUTLINE = 2
        PADDING = 10
        if id == 0:
            pass
        else:
            if id == 1:
                color = P1_CLR
            else:
                color = P2_CLR
            x = BOARD_CELL_SIZE[0] * col + BOARD_CELL_SIZE[0]
            y = BOARD_CELL_SIZE[1] * row + BOARD_CELL_SIZE[1]
            radius = BOARD_CELL_SIZE[0] // 2 - PADDING
            pygame.draw.circle(win, TOKEN_CLR_OUTLINE, (x, y), radius + OUTLINE)
            pygame.draw.circle(win, color, (x, y), radius)


    # Move the piece at target_value to (row,col)
    def move(self, target_value, row, col):
        self.board_state[row][col], self.board_state[target_value[0]][target_value[1]]  = self.board_state[target_value[0]][target_value[1]], 0


    def get_valid_moves(self, row,col):
        valid_moves = {}
        moves, found_cannon = self.check_soldier_move(row, col)
        valid_moves.update(moves)

        return valid_moves, found_cannon


    def check_soldier_move(self, row,col):
        found_cannon = False
        self.soldier_capture = 0
        self.cannon_capture = 0
        # Ignore moves for the towns
        if (row,col) in self.town_pos:
            return {}, found_cannon

        piece = self.get_piece((row,col))
        if piece == 1:
            self.turn = 1
            direction_mod = 1
        else:
            self.turn = 2
            direction_mod = -1

        # create three frontal postitions for basic move
        front_row = row +direction_mod
        if  front_row <= BOARD_ROWS-1 and  front_row >= 0:
            frontal_positions = [(front_row, col + i) for i in [-1,0,1] if col+i <= BOARD_ROWS-1 and col+i >= 0]

        else: frontal_positions = []
        side_positions = [(row, col+i) for i in [-1,1] if col+i <= BOARD_ROWS-1 and col+i >= 0]
        side_positions.extend(frontal_positions)

        moves = {}
        adj_friendly_pos = []
        allow_retreat = False

        # Check front and side positions -> if we find a friendly look for cannon
        for pos in side_positions:
            adj_piece = self.board_state[pos[0]][pos[1]]
            if adj_piece != 0:
                if adj_piece != piece:
                    moves[pos] = (row, col)
                    allow_retreat = True
                    self.soldier_capture+=1
                else:
                    # Found a friendly in front or side positions -> see if we can combine this to a cannon
                    adj_friendly_pos.append(pos)
                    cannon_moves = self.search_cannon2(piece, pos, row, col)
                    if cannon_moves:
                        moves.update(cannon_moves)
                        found_cannon = True

            # Not allowed to set non sitewards move when field is empty
            elif pos[0] != row:
                moves[pos] = (row, col)

        # Checking the back only needed for checking retreats
        if not allow_retreat:
            back_row = row - direction_mod
            if back_row <= BOARD_ROWS - 1 and back_row >= 0:
                back_positions = [(back_row, col + i) for i in [-1, 0, 1] if col + i <= BOARD_ROWS - 1 and col + i >= 0]
            else:
                back_positions = []

            for pos in back_positions:
                adj_piece = self.board_state[pos[0]][pos[1]]
                if adj_piece != 0 and adj_piece != piece:
                        allow_retreat = True

        if allow_retreat:
            moves.update(self.check_soldier_retreat(row,col, direction_mod))

        return moves, found_cannon


    def search_cannon2(self, piece,pos, row, col):
        moves = {}
        opposite_dir_vec = self.substract_tuples((row,col), pos)
        opposite_pos = self.add_tuples((row,col), opposite_dir_vec)

        if self.check_boundary(opposite_pos):
            adj_piece = self.get_piece(opposite_pos)
            if adj_piece != 0 and adj_piece == piece:
                # Found three piece row
                look_ahead_back = self.add_tuples(opposite_pos, opposite_dir_vec)
                look_ahead_front =  self.substract_tuples(pos, opposite_dir_vec)

                # Check front
                if self.check_boundary(look_ahead_front) and self.get_piece(look_ahead_front) == 0:
                    # only checking for move so if the field is empty
                    # if I also want to check for cannon formation check ahead_piece.color != piece.color
                    # slide move front
                    moves[look_ahead_front] = opposite_pos
                    look_ahead_front_further = self.substract_tuples(look_ahead_front, opposite_dir_vec)
                    if self.check_boundary(look_ahead_front_further):
                        p = self.get_piece(look_ahead_front_further)
                        if p!=0 and p != piece:
                            moves[look_ahead_front_further] = 0
                            self.cannon_capture+=1
                        # Only check additional move if the last one was in bounds
                        look_ahead_front_further = self.substract_tuples(look_ahead_front_further, opposite_dir_vec)
                        if self.check_boundary(look_ahead_front_further):
                            p = self.get_piece(look_ahead_front_further)
                            # p != piece checks piece color
                            if p!=0 and p != piece:
                                moves[look_ahead_front_further] = 0
                                self.cannon_capture+=1

                # Check back
                if self.check_boundary(look_ahead_back) and self.get_piece(look_ahead_back) == 0:
                    # only checking for move so if the field is empty
                    # if I also want to check for cannon formation check ahead_piece.color != piece.color
                    # slide move back
                    moves[look_ahead_back] = pos
                    look_ahead_back_further = self.add_tuples(look_ahead_back, opposite_dir_vec)
                    if self.check_boundary(look_ahead_back_further):
                        p = self.board_state[look_ahead_back_further[0]][look_ahead_back_further[1]]
                        if p != 0 and p != piece:
                            moves[look_ahead_back_further] = 0
                            self.cannon_capture += 1
                        # Only check additional move if the last one was in bounds
                        look_ahead_back_further = self.add_tuples(look_ahead_back_further, opposite_dir_vec)
                        if self.check_boundary(look_ahead_back_further):
                            p = self.board_state[look_ahead_back_further[0]][look_ahead_back_further[1]]
                            if p != 0 and p != piece:
                                moves[look_ahead_back_further] = 0
                                self.cannon_capture += 1
        return moves


    def check_soldier_retreat(self, row,col, direction_mod):
        moves = {}
        if row + (direction_mod * -2) <= BOARD_ROWS-1 and  row +(direction_mod *-2)>= 0:
            retreat_positions = [(row + (direction_mod *-2), col + i) for i in [-2,0,2] if col+i <= BOARD_ROWS-1 and col+i >= 0]
        else:
            return {}

        for pos in retreat_positions:
            # Is the target pos empty
            if self.get_piece(pos) == 0:
                # Is the position in between empty
                if self.board_state[self.mean(row, pos[0])][self.mean(col, pos[1])] == 0:
                    moves[pos] = (row,col)
            else:
                continue

        return moves

    def winner(self, board = False):
        if board:
            self.board_state = board
        for pos in self.town_pos:
            if self.get_piece(pos) != self.town_pos[pos]:
                return self.turn



    def check_boundary(self, pos):
        # If the enemy looks up the town
        if (pos[0] == 0 and self.turn == 2) or (pos[0] == 9 and self.turn == 1):
            if self.town_pos.get(pos) != self.turn:
                return True
        elif 0 <= pos[0] <= BOARD_ROWS - 1 and 0 <= pos[1] <= BOARD_ROWS - 1 and pos not in self.town_pos:
            return True
        else:
            return False
    def add_tuples(self,tup1,tup2):
        return(tup1[0] + tup2[0], tup1[1] + tup2[1])
    def substract_tuples(self,tup1,tup2):
        return(tup1[0] - tup2[0], tup1[1] - tup2[1])
    def mean(self,num1, num2):
        return (num1 + num2) //2
    def get_piece(self, tuple_input):
        row, col = tuple_input
        return self.board_state[row][col]

    # TODO remove function is not called so p1.left is not updated
    def remove(self, piece):
        self.board_state[piece.row][piece.col] = 0
        if piece.color == P1_CLR:
            self.p1_left -= 1
        else:
            self.p2_left -= 1

    def get_all_moves(self,player_num):
        all_cannons = 0
        all_moves = 0
        for pos in self.get_all_pieces(self.turn):
            moves, found_cannon = self.get_valid_moves(pos[0],pos[1])
            all_moves+=len(moves)
            all_cannons+= found_cannon

        print("cannons "+str(all_cannons))
        print("moves "+str(all_moves))

    def get_all_pieces(self, player_num):
        return np.asarray(np.where(np.array(self.board_state) == player_num)).T





