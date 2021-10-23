from copy import deepcopy
from AlphaBeta.transposition_table import TranspositionTable
import numpy as np


class AlphaBeta():
    def __init__(self, board):
        # Will be altered
        self.copy_board = deepcopy(board)
        # Needed to reconstruct boardstates
        self.orig_board = deepcopy(board.board_state)
        # Transposition Table
        self.TT = TranspositionTable(self.orig_board)

        #Evals
        self.num_moves = 0
        self.num_cannons = 0
        self.cannon_capture = 0
        self.soldier_capture = 0
        self.counter = 0


    def get_all_move_sequencesTT(self, seq, player_num):
        self.num_cannons = 0
        self.num_moves = 0
        self.cannon_capture = 0
        self.soldier_capture = 0
        output_sequence = []
        capture_bools = []
        # If there is a sequence simulate the resulting board state
        if seq:
            self.simulate_board(seq)

        for pos in self.copy_board.get_all_pieces(player_num):
            moves, found_cannon = self.copy_board.get_valid_moves(pos[0], pos[1])
            self.num_moves += len(moves)
            self.num_cannons += found_cannon
            self.cannon_capture+= self.copy_board.cannon_capture
            self.soldier_capture+= self.copy_board.soldier_capture
            capture_bools.extend([True if self.copy_board.get_piece(pos) != player_num and self.copy_board.get_piece(pos) != 0 else False for pos in moves])
            # TODO implement this directly into get_valid_moves to save on the extra loop
            output_sequence.extend([seq + i for i in list(moves.items())])
        print(f"created moves {capture_bools}")
        return zip(output_sequence, capture_bools)

    def get_all_move_sequences(self, seq, player_num):
        self.num_cannons = 0
        self.num_moves = 0
        self.cannon_capture = 0
        self.soldier_capture = 0
        output_sequence = []
        # If there is a sequence simulate the resulting board state
        if seq:
            self.simulate_board(seq)

        for pos in self.copy_board.get_all_pieces(player_num):
            moves, found_cannon = self.copy_board.get_valid_moves(pos[0], pos[1])
            self.num_moves += len(moves)
            self.num_cannons += found_cannon
            self.cannon_capture+= self.copy_board.cannon_capture
            self.soldier_capture+= self.copy_board.soldier_capture
            # TODO implement this directly into get_valid_moves to save on the extra loop
            output_sequence.extend([seq + i for i in list(moves.items())])
        return output_sequence

    def simulate_board(self, seq):
        # Given a sequence of moves starting from the root simulate its board state
        self.copy_board.board_state = deepcopy(self.orig_board)
        #print(f"orig board {self.orig_board.copy()}")
        for i,k in zip(seq[0::2], seq[1::2]):
            if k == 0:
                self.copy_board.board_state[i[0]][i[1]] = 0
            else:
                #print(f"from {k}")
                #print(f"to {i}")

                self.copy_board.move(k, i[0], i[1])
        #print(self.copy_board.board_state)
        #print("##########")

    # TODO check if we can shortcut this somehow
    def evaluate(self,seq):
        self.counter+=1

        # Needed to run again to find cannons and num of moves
        _ = self.get_all_move_sequences(seq, 1)
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

        return int(eval)

########################################################################################################################

    def minimax(self, depth, max_player, seq):
        if depth == 0 or self.copy_board.winner() != None:
            return self.evaluate(seq), self.copy_board.board_state

        if max_player:
            maxEval = float('-inf')
            best_move = None
            for move_seq in self.get_all_move_sequences(seq, 1):
                evaluation = self.minimax(depth - 1, False, move_seq)[0]
                maxEval = max(maxEval, evaluation)

                if maxEval == evaluation:
                    best_move = move_seq

            return maxEval, best_move
        else:
            minEval = float('inf')
            best_move = None
            for move_seq in self.get_all_move_sequences(seq, 2):
                evaluation = self.minimax(depth - 1, True, move_seq)[0]
                minEval = min(minEval, evaluation)

                if minEval == evaluation:
                    best_move = move_seq

            return minEval, best_move

########################################################################################################################

    def alphabeta(self, depth, alpha, beta, player, seq = ()):
        if depth == 0 or self.copy_board.winner() != None:
            return self.evaluate(seq), seq
        score = float("-inf")

        for move_seq in self.get_all_move_sequences(seq, player):
            if player == 1: player = 2
            else: player = 1
            value = -self.alphabeta(depth-1, -beta, -alpha, player, move_seq)[0]
            if(value > score):
                score = value
                bestMove = move_seq
            if(score > alpha): alpha = score
            if(score >= beta): break
        return score, bestMove

########################################################################################################################

    def alphabeta_TT(self, depth, alpha, beta, player, key, seq = (), capture_bool = False):
        origAlpha = alpha
        # TT Lookup
        ttEntry = self.TT.retrieve(key,seq, player, capture_bool)
        if ttEntry and ttEntry.depth >= depth:
            print("in tt")
            # Exact
            if ttEntry.flag == 0:
                return ttEntry.value, ttEntry.move
            # LowerBound
            elif ttEntry.flag == 1:
                alpha = max(alpha, ttEntry.value)
            # UpperBound
            else:
                beta = min(beta, ttEntry.value)
            if alpha >= beta:
                return ttEntry.value, ttEntry.move


        # Alpha Beta
        if depth == 0 or self.copy_board.winner() != None:
            return self.evaluate(seq), seq
        score = float("-inf")
        for move_seq, capture_bool in self.get_all_move_sequencesTT(seq, player):
            if player == 1: player = 2
            else: player = 1
            # TODO does the key make sense here?
            value = -self.alphabeta_TT(depth-1, -beta, -alpha, player,key, move_seq, capture_bool)[0]
            if(value > score):
                score = value
                bestMove = move_seq
            if(score > alpha): alpha = score
            if(score >= beta): break

        # TT saving
        # UpperBound
        if score <= origAlpha:
            flag = 2
        # LowerBound
        elif score >= beta:
            flag = 1
        # Exact
        else:
            flag = 0
        # TODO how to get capture bool here
        print(self.TT.t_table)
        self.TT.store(bestMove, score, flag, depth, key, seq, player, capture_bool)

        return score, bestMove












