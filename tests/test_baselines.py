"""Tests for the baseline bots in src/baselines.py."""

import unittest

from src.baselines import GreedyBot
from src.board import Board


def play_all(board, moves):
    for col in moves:
        board.play(col)


class TestGreedyBot(unittest.TestCase):
    def test_takes_immediate_win(self):
        board = Board()
        play_all(board, [0, 0, 1, 1, 2, 6])

        self.assertEqual(GreedyBot(seed=0).choose_move(board), 3)

    def test_blocks_opponent_immediate_win(self):
        board = Board()
        play_all(board, [0, 0, 1, 1, 2])

        self.assertEqual(GreedyBot(seed=0).choose_move(board), 3)

    def test_winning_move_takes_priority_over_block(self):
        board = Board()
        # Player 1 can win in column 3, while player 2 threatens vertically in 6.
        board.grid[5][0:3] = [1, 1, 1]
        board.grid[3][6] = 2
        board.grid[4][6] = 2
        board.grid[5][6] = 2
        board.current_player = 1

        self.assertEqual(GreedyBot(seed=0).choose_move(board), 3)

    def test_does_not_change_board(self):
        board = Board()
        play_all(board, [3, 2, 4, 1])
        before = [row[:] for row in board.grid]
        current_player = board.current_player

        GreedyBot(seed=0).choose_move(board)

        self.assertEqual(board.grid, before)
        self.assertEqual(board.current_player, current_player)

    def test_falls_back_to_random_legal_move(self):
        bot = GreedyBot(seed=0)
        board = Board()

        move = bot.choose_move(board)

        self.assertIn(move, board.valid_moves())


if __name__ == "__main__":
    unittest.main()
