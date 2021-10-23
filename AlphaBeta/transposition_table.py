import random

class TranspositionTable():
    def __init__(self, board_state):
        self.z_table = self.init_zobrist_table()
        self.p_move = [random.getrandbits(64),random.getrandbits(64)]
        self.z_key = self.generate_initial_key(board_state)
        self.t_table = {}

    # Generate the table of random values for zobrist hashing
    def init_zobrist_table(self):
        col_num = 10
        row_num = 10
        zobrist_table = [[[None] * 2 for _ in range(row_num)] for _ in range(col_num)]

        for row in range(row_num):
            for col in range(col_num):
                for i in range(2):
                    zobrist_table[row][col][i] = random.getrandbits(64)

        return zobrist_table

    # Generate a zobrist key based on the inital board state
    def generate_initial_key(self, board_state):
        z_key = 0
        for row in range(10):
            for col in range(10):
                piece = board_state[row][col]
                if piece == 1:
                    z_key = z_key ^ self.z_table[row][col][0]
                else:
                    z_key = z_key ^ self.z_table[row][col][0]

        z_key = z_key ^ self.p_move[0]
        return z_key


    def update_key(self, key, move, player_num, capture_bool):
        # given a move of form ((x,x),(y,y,)) or ((x,x),0)
        if player_num == 1: enemy_num = 2
        else: enemy_num = 1
        # Cannon shot -> XOR the enemey's position
        print(f"move in tt {move}")
        if move[1] == 0:
            key = key ^ self.z_table[move[0][0]][move[0][1]][enemy_num-1]
        # Capture move -> XOR enemey's position, players old position, players new position
        elif capture_bool:
            key = key ^ self.z_table[move[0][0]][move[0][1]][enemy_num-1]
            key = key ^ self.z_table[move[0][0]][move[0][1]][player_num-1]
            key = key ^ self.z_table[move[1][0]][move[1][1]][player_num-1]
        # Normal move -> XOR players old position, players new position
        else:
            self.z_key = self.z_key ^ self.z_table[move[0][0]][move[0][1]][player_num-1]
            self.z_key = self.z_key ^ self.z_table[move[1][0]][move[1][1]][player_num-1]
        return key

    def retrieve(self, key, move, player_num, capture_bool):
        if move:
            move = move[-2:]
            key = self.update_key(key, move, player_num, capture_bool)
            return self.t_table.get(key)

    def store(self, bestMove, bestValue, flag, depth, key, move, player_num, capture_bool):
        key = self.update_key(key, move, player_num, capture_bool)
        self.t_table[key] = TT_entry(bestMove, bestValue, flag, depth)

class TT_entry():
    def __init__(self, bestMove, bestValue, flag, depth):
        self.move = bestMove
        self.value = bestValue
        self.flag = flag
        self.depth = depth

