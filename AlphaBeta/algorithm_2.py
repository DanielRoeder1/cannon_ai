from copy import deepcopy
import numpy as np

class AlphaBeta2():
    def __init__(self, board):
        # Will be altered
        self.copy_board = deepcopy(board)

        #Evals
        self.num_moves = 0
        self.num_cannons = 0
        self.cannon_capture = 0
        self.soldier_capture = 0
        self.counter = 0

    def get_all_moves(self, board, player_num):
        sim_boards = []
        self.num_cannons = 0
        self.num_moves = 0
        self.cannon_capture = 0
        self.soldier_capture = 0

        self.copy_board.board_state = board

        for pos in self.copy_board.get_all_pieces(player_num):
            moves, found_cannon = self.copy_board.get_valid_moves(pos[0], pos[1])

            # Evlas
            self.num_moves += len(moves)
            self.num_cannons += found_cannon
            self.cannon_capture+= self.copy_board.cannon_capture
            self.soldier_capture+= self.copy_board.soldier_capture
            # Simulate the board
            for move in moves:
                sim_boards.append(self.simulate_move((move,moves.get(move))))
        return sim_boards


    def simulate_move(self, move):

        tmp_board = deepcopy(self.copy_board.board_state)
        if move[1] == 0:
            tmp_board[move[0][0]][move[0][1]] = 0
        else:
            tmp_board[move[0][0]][move[0][1]], tmp_board[move[1][0]][move[1][1]] = tmp_board[move[1][0]][move[1][1]], 0

        return tmp_board


    def evaluate(self,board):
        self.counter+=1

        # Needed to run again to find cannons and num of moves
        _ = self.get_all_moves(board,1)
        # Get number of stones on the board
        # -1 for the towns
        my_stones = self.copy_board.get_all_pieces(1)
        num_enemy_stones =  len(self.copy_board.get_all_pieces(2))
        num_my_stones = len(my_stones)

        average_row = np.mean(np.array(my_stones)[:,0])
        # print(average_row)
        # print(my_stones)
        # print(self.num_moves)
        # print(self.num_cannons)
        # print(self.cannon_capture)
        # print(self.soldier_capture)


        eval = 100 * (num_my_stones - num_enemy_stones) + 0.5 *self.num_moves + 9 *self.num_cannons + 10 *self.cannon_capture + 10 *self.soldier_capture + 100 * average_row
        #print(eval)
        return eval

    def alphabeta(self, board, depth, alpha, beta , player_num):
        if depth == 0 or self.copy_board.winner(board) != None:
            return self.evaluate(board), board
        score = float("-inf")
        for sim_board in self.get_all_moves(board, player_num):
            if player_num == 1: player_num = 2
            else: player_num = 1
            value = -self.alphabeta(sim_board, depth-1, -beta, -alpha, player_num)[0]
            if(value > score):
                score = value
                bestBoard = sim_board
            if(score > alpha): alpha = score
            if(score >= beta): break
        return score, bestBoard