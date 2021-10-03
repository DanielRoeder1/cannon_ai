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

    def get_piece(self, row, col):
        return self.board_state[row][col]

    # Change state representation with move
    def move(self, piece, row, col):
        self.board_state[piece.row][piece.col], self.board_state[row][col] = self.board_state[row][col], self.board_state[piece.row][piece.col]
        piece.move(row, col)

    def get_valid_moves(self, piece):
        valid_moves = {}
        valid_moves.update(self.check_soldier_move(piece))

        return valid_moves


    # Check for the basic step and capture move
    def check_soldier_move(self, piece):
        moves = {}
        adj_friendly_pos = []
        # Which direction to go
        if piece.color == P1_CLR:
            direction_mod = 1
        else:
            direction_mod = -1

        # create three frontal postitions for basic move
        front_row = piece.row +direction_mod
        if  front_row <= BOARD_ROWS-1 and  front_row >= 0:
            frontal_positions = [(front_row, piece.col + i) for i in range(-1,2) if piece.col+i <= BOARD_ROWS-1 and piece.col+i >= 0]
        else: frontal_positions = []
        side_positions = [(piece.row, piece.col+i) for i in [-1,1] if piece.col+i <= BOARD_ROWS-1 and piece.col+i >= 0]

        side_positions.extend(frontal_positions)

        for pos in side_positions:
            adj_piece = self.board_state[pos[0]][pos[1]]
            if adj_piece != 0:
                if adj_piece.color != piece.color:
                    moves[pos] = True
                    moves.update(self.check_soldier_retreat(piece, direction_mod))
                else:
                    # This method already checks the front and sides for friendly only need to handle back in check_cannon
                    adj_friendly_pos.append(pos)
            elif pos[0] != piece.row:
                moves[pos] = False
        print(f"adjacent friendly begin: {adj_friendly_pos}")
        self.check_cannon(piece, adj_friendly_pos, direction_mod)
        return moves


    def check_cannon(self, piece, adj_friendly_pos, direction_mod):
        moves = {}
        cols_checked = [(piece.col - pos[1]) for pos in adj_friendly_pos]
        if piece.row -direction_mod <= BOARD_ROWS-1 and  piece.row -direction_mod >= 0:
            back_positions = [(piece.row - direction_mod, piece.col + i) for i in range(-1,2) if piece.col+i <= BOARD_ROWS-1 and piece.col+i >= 0 and i not in cols_checked]

        for pos in back_positions:
            adj_piece = self.board_state[pos[0]][pos[1]]
            if adj_piece !=0 and adj_piece.color == piece.color:
                adj_friendly_pos.append(pos)

        cannon_formations = []
        for friendly_pos in adj_friendly_pos:
            result = self.search_cannon(friendly_pos, piece, adj_friendly_pos)
            if result:
                cannon_formations.extend(result)
        print(cannon_formations)

    # TODO maybe only search for cannon formation where the selected piece is in a leading position
    # TODO adj_friendly_pos isnt used?
    # takes the friendlies already found in check cannon and extends the search such that all cannon structures for a given token are found
    def search_cannon(self, friendly_pos, piece,adj_friendly_pos):
        print(f"friendly pos: {friendly_pos}")
        print("begin "+str(adj_friendly_pos))
        friendly_pos_found = [friendly_pos, (piece.row, piece.col)]
        rel_cannon_dir = (friendly_pos[0] - piece.row, friendly_pos[1] - piece.col)

        # Search towards the front: from piece found in previous step onwards
        for i in range(1,8):
            print(i)
            try:
                new_pos = (friendly_pos[0] + rel_cannon_dir[0] *i,friendly_pos[1] + rel_cannon_dir[1] *i)
                adj_piece = self.board_state[new_pos[0]][new_pos[1]]
                if adj_piece != 0 and adj_piece.color == piece.color:
                    friendly_pos_found.append(new_pos)
                else:
                    break
            except:
                break
        print("middle: " + str(friendly_pos_found))
        # search in the opposite direction starting from the central piece
        for i in range(1,8):
            print(i)
            try:
                new_pos = (piece.row - rel_cannon_dir[0] *i,piece.col - rel_cannon_dir[1] *i)
                adj_piece = self.board_state[new_pos[0]][new_pos[1]]
                if adj_piece != 0 and adj_piece.color == piece.color and (adj_piece.row,adj_piece.col) not in adj_friendly_pos:
                    friendly_pos_found.append(new_pos)
                else:
                    break
            except:
                break
        friendly_pos_found = sorted(friendly_pos_found, key = sum)
        print("final: "+str(friendly_pos_found))
        if len(friendly_pos_found) == 3:
            return [friendly_pos_found]
        elif len(friendly_pos_found) > 3:
            return [friendly_pos_found[:3],friendly_pos_found[-3:]]

    def cannon_movement(self):
        pass


    # Check for the retreat move
    def check_soldier_retreat(self, piece, direction_mod):
        moves = {}
        if piece.row + (direction_mod * -2) <= BOARD_ROWS-1 and  piece.row +(direction_mod *-2)>= 0:
            retreat_positions = [(piece.row + (direction_mod *-2), piece.col + i) for i in [-2,0,2] if piece.col+i <= BOARD_ROWS-1 and piece.col+i >= 0]
        else:
            return {}

        for pos in retreat_positions:
            if self.board_state[pos[0]][pos[1]] == 0:
                if self.board_state[self.mean(piece.row, pos[0])][self.mean(piece.col, pos[1])] == 0:
                    moves[pos] = False
            else:
                continue

        return moves



    def mean(self,num1, num2):
        return (num1 + num2) //2

    def remove(self, piece):
        self.board_state[piece.row][piece.col] = 0
        if piece.color == P1_CLR:
            self.p1_left -= 1
        else:
            self.p2_left -= 1






