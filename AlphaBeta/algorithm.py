from copy import deepcopy
import pygame
from cannon.board import Board
import numpy as np
class AlphaBeta():
    def __init__(self, board):
        # Will be altered
        self.copy_board = deepcopy(board)
        # Needed to reconstruct boardstates
        self.orig_board = board.board_state
        #Evals
        self.num_moves = 0
        self.num_cannons = 0

    def get_all_move_sequences(self, seq, player_num):
        self.num_cannons = 0
        self.num_moves = 0
        output_sequence = []
        # If there is a sequence simulate the resulting board state
        if seq:
            self.simulate_board(seq)

        for pos in self.copy_board.get_all_pieces(player_num):
            moves, found_cannon = self.copy_board.get_valid_moves(pos[0], pos[1])
            self.num_moves += len(moves)
            self.num_cannons += found_cannon
            # TODO implement this directly into get_valid_moves to save on the extra loop
            output_sequence.extend([seq + i for i in list(moves.items())])
        print(output_sequence)
        return output_sequence

    def simulate_board(self, seq):
        # Given a sequence of moves starting from the root simulate its board state
        self.copy_board.board_state = self.orig_board.copy()
        for i,k in zip(seq[0::2], seq[1::2]):
            if k == 0:
                self.copy_board.board_state[i[0], i[1]] = 0
            else:
                self.copy_board.move(i, k[0], k [1])

    # TODO check if we can shortcut this somehow
    def evaluate(self,seq, max_player):
        if max_player:
            player_num = 1
        else:
            player_num = 2

        # Needed to run again to find cannons and num of moves
        _ = self.get_all_move_sequences(seq, player_num)
        # Get number of stones on the board
        # -1 for the towns
        my_stones = sum(i.count(1) for i in self.copy_board.board_state) -1
        enemy_stones = sum(i.count(2) for i in self.copy_board.board_state) -1
        eval = (my_stones - enemy_stones) + 0.8 *self.num_moves + 9 *self.num_cannons
        return eval

    def minimax(self, depth, max_player, seq):
        if depth == 0 or self.copy_board.winner() != None:
            return self.evaluate(seq,max_player), self.copy_board.board_state

        if max_player:
            maxEval = float('-inf')
            best_move = None
            for move_seq in self.get_all_move_sequences(seq, 1):
                evaluation, move = self.minimax(depth - 1, False, move_seq)
                maxEval = max(maxEval, evaluation)
                print("!!!!!!!!!!")
                print(move)
                print("!!!!!!!!!!")

                if maxEval == evaluation:
                    best_move = move

            return maxEval, best_move
        else:
            minEval = float('inf')
            best_move = None
            for move_seq in self.get_all_move_sequences(seq, 2):
                evaluation, move = self.minimax(depth - 1, True, move_seq)
                minEval = min(minEval, evaluation)
                print("!!!!!!!!!!")
                print(move)
                print("!!!!!!!!!!")
                if minEval == evaluation:
                    best_move = move

            return minEval, best_move













def get_all_moves(board, player_num):
    all_moves = {}
    num_cannons = 0
    num_moves = 0
    for pos in board.get_all_pieces(player_num):
        moves, found_cannon = board.get_valid_moves(pos[0],pos[1])
        num_moves+=len(moves)
        num_cannons+= found_cannon
        all_moves.update(moves)

    print("cannons "+str(num_cannons))
    print("moves "+str(num_moves))
    print(all_moves)
    return all_moves


