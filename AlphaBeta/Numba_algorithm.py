from numba import jit
from copy import deepcopy
import numpy as np
import random


@jit(nopython=True)
def get_valid_moves(board_state, player_num, eval_bool, town_pos):
    # Init
    BOARD_ROWS = 10
    moves = []
    capture_bools = []
    capture_moves = []
    allow_retreat = False
    soldier_capture = 0
    cannons_found = 0
    cannon_captures = 0

    # Direction in which to move
    if player_num == 1:
        direction_mod = 1
    else:
        direction_mod = -1

    # Iterate over all pieces from this player
    rows, cols = np.where(board_state == player_num)
    num_pieces = len(rows)
    avg_row = np.mean(rows)

    for row, col in zip(rows, cols):
        if (town_pos[0][0] == row and town_pos[0][1] == col) or (town_pos[1][0] == row and town_pos[1][1] == col):
            continue
        # Create front and side positions
        side_positions = [(row, col + i) for i in [-1, 1] if col + i <= BOARD_ROWS - 1 and col + i >= 0]
        front_row = row + direction_mod
        if front_row <= BOARD_ROWS - 1 and front_row >= 0:
            frontal_positions = [(front_row, col + i) for i in [-1, 0, 1] if col + i <= BOARD_ROWS - 1 and col + i >= 0]
            side_positions.extend(frontal_positions)

        for pos in side_positions:
            adj_piece = board_state[pos[0]][pos[1]]
            if adj_piece != 0:
                # Enemy found
                if adj_piece != player_num:
                    if not eval_bool:
                        boards, capture_bool = simulate_board(board_state, pos, row, col, player_num)
                        capture_moves.append(boards)
                        capture_bools.append(capture_bool)
                    allow_retreat = True
                    soldier_capture += 1
                # Friendly found
                else:
                    cannon_moves, num_cannon_captures, capture_bools_cannon, capture_moves_cannon = generate_cannon_moves(
                        board_state, row, col, pos, player_num, eval_bool, town_pos)
                    moves.extend(cannon_moves)
                    capture_moves.extend(capture_moves_cannon)
                    capture_bools.extend(capture_bools_cannon)
                    if len(cannon_moves) > 0:
                        cannons_found += 1
                    cannon_captures += num_cannon_captures

            elif pos[0] != row:
                if not eval_bool:
                    boards, capture_bool = simulate_board(board_state, pos, row, col, player_num)
                    moves.append(boards)
                    capture_bools.append(capture_bool)

        if not allow_retreat:
            back_row = row - direction_mod
            if back_row <= BOARD_ROWS - 1 and back_row >= 0:
                for i in [-1, 0, 1]:
                    if col + i <= BOARD_ROWS - 1 and col + i >= 0:
                        adj_piece = board_state[back_row][col + i]
                        if adj_piece != 0 and adj_piece != player_num:
                            allow_retreat = True

        if allow_retreat and not eval_bool:
            boards, capture_bools_retreat = check_soldier_retreat(row, col, direction_mod, board_state, player_num)
            moves.extend(boards)
            capture_bools.extend(capture_bools_retreat)

    moves = capture_moves + moves
    return moves, soldier_capture, cannons_found, cannon_captures, num_pieces, avg_row


@jit(nopython=True)
def generate_cannon_moves(board_state, row, col, pos, player_num, eval_bool, town_pos):
    moves = []
    capture_bools = []
    capture_moves = []
    cannon_capture = 0
    pos_n = np.array(pos)
    pos2_n = np.array((row, col))

    opposite_dir_vec = pos2_n - pos_n
    opposite_pos = pos2_n + opposite_dir_vec

    if check_boundary(opposite_pos, player_num, town_pos):
        adj_piece = board_state[opposite_pos[0]][opposite_pos[1]]
        if adj_piece != 0 and adj_piece == player_num:
            look_ahead_back = opposite_pos + opposite_dir_vec
            look_ahead_front = pos_n - opposite_dir_vec

            if check_boundary(look_ahead_front, player_num, town_pos) and board_state[look_ahead_front[0]][
                look_ahead_front[1]] == 0:
                # Front slide
                if not eval_bool:
                    boards, capture_bool = simulate_board(board_state, look_ahead_front, opposite_pos[0],
                                                          opposite_pos[1], player_num)
                    moves.append(boards)
                    capture_bools.append(capture_bool)

                # Front Cannon Shots
                look_ahead_front_further = look_ahead_front - opposite_dir_vec
                if check_boundary(look_ahead_front_further, player_num, town_pos):
                    p = board_state[look_ahead_front_further[0]][look_ahead_front_further[1]]
                    if p != 0 and p != player_num:
                        if not eval_bool:
                            boards, capture_bool = simulate_board(board_state, look_ahead_front_further, 0, 0,
                                                                  player_num)
                            capture_moves.append(boards)
                            capture_bools.append(capture_bool)
                        cannon_capture += 1
                    look_ahead_front_further = look_ahead_front_further - opposite_dir_vec
                    if check_boundary(look_ahead_front_further, player_num, town_pos):
                        p = board_state[look_ahead_front_further[0]][look_ahead_front_further[1]]
                        if p != 0 and p != player_num:
                            if not eval_bool:
                                boards, capture_bool = simulate_board(board_state, look_ahead_front_further, 0, 0,
                                                                      player_num)
                                capture_moves.append(boards)
                                capture_bools.append(capture_bool)
                            cannon_capture += 1

            if check_boundary(look_ahead_back, player_num, town_pos) and board_state[look_ahead_back[0]][
                look_ahead_back[1]] == 0:
                # Back slide
                if not eval_bool:
                    boards, capture_bool = simulate_board(board_state, look_ahead_back, pos[0], pos[1], player_num)
                    moves.append(boards)
                    capture_bools.append(capture_bool)

                # Back Cannon Shots
                look_ahead_back_further = look_ahead_back + opposite_dir_vec
                if check_boundary(look_ahead_back_further, player_num, town_pos):
                    p = board_state[look_ahead_back_further[0]][look_ahead_back_further[1]]
                    if p != 0 and p != player_num:
                        if not eval_bool:
                            boards, capture_bool = simulate_board(board_state, look_ahead_back_further, 0, 0,
                                                                  player_num)
                            capture_moves.append(boards)
                            capture_bools.append(capture_bool)
                        cannon_capture += 1
                    look_ahead_back_further = look_ahead_back_further + opposite_dir_vec
                    if check_boundary(look_ahead_back_further, player_num, town_pos):
                        p = board_state[look_ahead_back_further[0]][look_ahead_back_further[1]]
                        if p != 0 and p != player_num:
                            if not eval_bool:
                                boards, capture_bool = simulate_board(board_state, look_ahead_back_further, 0, 0,
                                                                      player_num)
                                capture_moves.append(boards)
                                capture_bools.append(capture_bool)
                            cannon_capture += 1
    return moves, cannon_capture, capture_bools, capture_moves


@jit(nopython=True)
def check_soldier_retreat(row, col, direction_mod, board_state, player_num):
    moves = []
    capture_bools = []
    if row + (direction_mod * -2) <= 10 - 1 and row + (direction_mod * -2) >= 0:
        for i in [-2, 0, 2]:
            if col + i <= 10 - 1 and col + i >= 0:
                row_retreat = row + direction_mod * -2
                col_retreat = col + i

                if board_state[row_retreat][col_retreat] == 0:
                    if board_state[mean(row, row_retreat)][mean(col, col_retreat)] == 0:
                        boards, capture_bool = simulate_board(board_state, (row_retreat, col_retreat), row, col,
                                                              player_num)
                        moves.append(boards)
                        capture_bools.append(capture_bool)

                else:
                    continue
    return moves, capture_bools


@jit(nopython=True)
def check_boundary(pos, player_num, town_pos):
    if (pos[0] == 0 and player_num == 2) or (pos[0] == 9 and player_num == 1):
        for t_pos in town_pos:
            if t_pos[0] == pos[0] and t_pos[1] == pos[1]:
                if t_pos[2] != player_num:
                    return True
    if 0 <= pos[0] <= 10 - 1 and 0 <= pos[1] <= 10 - 1:
        return True
    else:
        return False


@jit(nopython=True)
def simulate_board(board, pos, row, col, player_num):
    capture_bool = False
    tmp_board = board.copy()
    if row == 0 and col == 0:
        tmp_board[pos[0]][pos[1]] = 0
        capture_bool = True
    elif tmp_board[pos[0]][pos[1]] != player_num:
        capture_bool = True
        tmp_board[pos[0]][pos[1]], tmp_board[row][col] = tmp_board[row][col], 0
    else:
        tmp_board[pos[0]][pos[1]], tmp_board[row][col] = tmp_board[row][col], 0

    # print("Output Board")
    # print(tmp_board)
    return tmp_board, capture_bool


@jit(nopython=True)
def mean(x1, x2):
    return (x1 + x2) // 2


@jit(nopython=True)
def winner(board_state, town_pos):
    # save townpos as [x,y,player_num]
    for pos in town_pos:
        if board_state[pos[0]][pos[1]] != pos[2]:
            return True
            # return False
        else:
            return False
            # return True


@jit(nopython=True)
def evaluate(board_state, town_pos):
    boards, soldier_capture, cannons_found, cannon_captures, num_pieces, avg_row = get_valid_moves(board_state, 1, True,
                                                                                                   town_pos)
    num_enemy_pieces = len(np.where(board_state == 2)[0])
    return 100 * (
                num_pieces - num_enemy_pieces) + 9 * cannons_found + 10 * cannon_captures + 10 * soldier_capture + 100 * avg_row


@jit(nopython=True)
def alphabeta(board_state, player_num, depth, alpha, beta, town_pos):
    if depth == 0 or winner(board_state, town_pos):
        return evaluate(board_state, town_pos), board_state

    # Switch players
    if player_num == 1:
        next_player = 2
    else:
        next_player = 1

    # float() unknown to numba
    score = -10000000
    for child_board in get_valid_moves(board_state, player_num, False, town_pos)[0]:
        value = -alphabeta(child_board, next_player, depth - 1, -beta, -alpha, town_pos)[0]

        if (value > score):
            score = value
            bestMove = child_board
        if (score > alpha): alpha = score
        if (score >= beta): break

    return score, bestMove


def alphabeta_TT(board_state, player_num, depth, alpha, beta, town_pos):
    # print(len(tt.t_table))
    old_a = alpha
    n = tt.retrieve(board_state)
    # n = (bestMove, score, flag, depth)
    if n and n[3] <= depth:
        # print(n[3])
        # print(depth)
        if n[2] == 0:
            return n[1], n[0]
        if n[2] == 1:
            alpha = max(alpha, n[1])
        else:
            beta = min(beta, n[1])
        if alpha >= beta:
            return n[1], n[0]

    if depth == 0 or winner(board_state, town_pos):
        multi = 1
        if player_num == 2:
            multi = -1
        return multi * evaluate(board_state, town_pos), board_state

    # Switch players
    if player_num == 1:
        next_player = 2
    else:
        next_player = 1

    # float() unknown to numba
    score = -10000000

    child_boards = get_valid_moves(board_state, player_num, False, town_pos)[0]
    # TT move ordering
    if n != None:
        child_boards = move_ordering(n[0], child_boards)

    for child_board in child_boards:
        value = -alphabeta_TT(child_board, next_player, depth - 1, -beta, -alpha, town_pos)[0]

        if (value > score):
            score = value
            bestMove = child_board
        if (score > alpha): alpha = score
        if (score >= beta): break

    if score <= old_a:
        flag = 2
    elif score >= beta:
        flag = 1
    else:
        flag = 0

    tt.store(board_state, bestMove, score, flag, depth)

    return score, bestMove


class TraspositionTable():
    def __init__(self, board_state):
        self.z_table = self.init_zobrist_table()
        self.p_move = np.array([random.getrandbits(60), random.getrandbits(60)], dtype=np.int64)
        self.t_table = {}

    def init_zobrist_table(self):
        col_num = 10
        row_num = 10
        zobrist_table = np.zeros((10, 10, 2), dtype=np.int64)

        for row in range(row_num):
            for col in range(col_num):
                for i in range(2):
                    zobrist_table[row][col][i] = random.getrandbits(60)

        return zobrist_table

    def store(self, board_state, bestMove, score, flag, depth):
        key = generate_key(self.z_table, board_state, self.p_move)
        self.t_table[key] = (bestMove, score, flag, depth)

    def retrieve(self, board_state):
        key = generate_key(self.z_table, board_state, self.p_move)
        return self.t_table.get(key)

    def clear(self):
        self.t_table = {}


@jit(nopython=True)
def generate_key(z_table, board_state, p_move):
    z_key = 0
    for row in range(10):
        for col in range(10):
            piece = board_state[row][col]
            if piece == 1:
                z_key = z_key ^ z_table[row][col][0]
            elif piece == 2:
                z_key = z_key ^ z_table[row][col][1]
    z_key = z_key ^ p_move[0]
    return z_key


def move_ordering(insert_v, target_list):
    for i in range(len(target_list)):
        if np.array_equal(target_list[i], insert_v):
            index = i
            break
    target_list.pop(1)
    target_list.insert(0, insert_v)
    return target_list

def init_board():
    board_state= np.zeros((10,10))
    for row in range(10):
        for col in range(10):
            if row in range(1,4) and col % 2 != 0:
                board_state[row,col] = 1
            elif row in range(6,9) and col % 2 == 0:
                board_state[row, col] = 2
    return board_state
x = init_board()


y = deepcopy(x)
y[0][0] = 1
y[9][9] = 2
town_pos = np.array([[0,0,1],[9,9,2]])
y

tt = TraspositionTable(y)

