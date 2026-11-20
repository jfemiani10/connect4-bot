"""Tests for the minimax bot in src/minimax.py.

Run all tests from the repo root with:
    python3 -m unittest
"""

import unittest

from src.baselines import RandomBot
from src.board import Board
from src.minimax import MinimaxBot, evaluate


def play_all(board, moves):
    """Play a list of columns in order (players alternate automatically)."""
    for col in moves:
        board.play(col)


class TestMinimax(unittest.TestCase):
    def test_takes_immediate_win(self):
        board = Board()
        # Player 1 has three in a row on the bottom (columns 0-2) and it's
        # player 1's turn, so playing column 3 wins.
        play_all(board, [0, 0, 1, 1, 2, 6])
        for depth in (1, 2, 4):
            self.assertEqual(MinimaxBot(depth=depth).choose_move(board), 3)

    def test_blocks_opponent_win(self):
        board = Board()
        # Player 1 has three in a row on the bottom (columns 0-2) and it's
        # player 2's turn. Column 3 is the only way to stop player 1 winning.
        play_all(board, [0, 0, 1, 1, 2])
        for depth in (2, 4):
            self.assertEqual(MinimaxBot(depth=depth).choose_move(board), 3)

    def test_does_not_change_board(self):
        board = Board()
        play_all(board, [3, 3, 2])
        before = [row[:] for row in board.grid]
        MinimaxBot(depth=3).choose_move(board)
        self.assertEqual(board.grid, before)

    def test_alpha_beta_picks_same_move_with_fewer_positions(self):
        # Pruning must never change the chosen move, only the work done.
        board = Board()
        play_all(board, [3, 2, 3, 4])
        plain = MinimaxBot(depth=4, alpha_beta=False)
        pruned = MinimaxBot(depth=4, alpha_beta=True)
        self.assertEqual(plain.choose_move(board), pruned.choose_move(board))
        self.assertLess(pruned.positions_searched, plain.positions_searched)

    def test_alpha_beta_matches_plain_over_many_positions(self):
        # Same check over positions from random games, for extra confidence.
        rng_bot = RandomBot(seed=0)
        for game in range(5):
            board = Board()
            while not board.game_over():
                plain = MinimaxBot(depth=3, alpha_beta=False).choose_move(board)
                pruned = MinimaxBot(depth=3, alpha_beta=True).choose_move(board)
                self.assertEqual(plain, pruned)
                board.play(rng_bot.choose_move(board))

    def test_evaluate_is_symmetric(self):
        # A position's score for one player is the negative of the other's.
        board = Board()
        play_all(board, [3, 2, 3, 4, 1])
        self.assertEqual(evaluate(board, 1), -evaluate(board, 2))

    def test_beats_random_bot(self):
        wins = 0
        for seed in range(10):
            board = Board()
            bots = {1: MinimaxBot(depth=3), 2: RandomBot(seed=seed)}
            while not board.game_over():
                board.play(bots[board.current_player].choose_move(board))
            wins += board.winner() == 1
        self.assertGreaterEqual(wins, 9)


if __name__ == "__main__":
    unittest.main()
