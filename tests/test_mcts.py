"""Tests for the MCTS bot in src/mcts.py.

Run all tests from the repo root with:
    python3 -m unittest
"""

import unittest

from src.baselines import RandomBot
from src.board import Board
from src.mcts import MCTSBot


def play_all(board, moves):
    """Play a list of columns in order (players alternate automatically)."""
    for col in moves:
        board.play(col)


class TestMCTS(unittest.TestCase):
    def test_takes_immediate_win(self):
        board = Board()
        # Player 1 has three in a row on the bottom (columns 0-2) and it's
        # player 1's turn, so playing column 3 wins.
        play_all(board, [0, 0, 1, 1, 2, 6])
        self.assertEqual(MCTSBot(iterations=1000, seed=0).choose_move(board), 3)

    def test_blocks_opponent_win(self):
        board = Board()
        # Player 1 has three in a row on the bottom (columns 0-2) and it's
        # player 2's turn. Column 3 is the only way to stop player 1 winning.
        play_all(board, [0, 0, 1, 1, 2])
        self.assertEqual(MCTSBot(iterations=1000, seed=0).choose_move(board), 3)

    def test_does_not_change_board(self):
        board = Board()
        play_all(board, [3, 3, 2])
        before = [row[:] for row in board.grid]
        MCTSBot(iterations=200, seed=0).choose_move(board)
        self.assertEqual(board.grid, before)

    def test_same_seed_same_move(self):
        # With a fixed seed, MCTS must be repeatable, so experiments can be rerun.
        board = Board()
        play_all(board, [3, 2])
        first = MCTSBot(iterations=300, seed=7).choose_move(board)
        second = MCTSBot(iterations=300, seed=7).choose_move(board)
        self.assertEqual(first, second)

    def test_beats_random_bot(self):
        wins = 0
        for seed in range(10):
            board = Board()
            bots = {1: MCTSBot(iterations=300, seed=seed), 2: RandomBot(seed=seed)}
            while not board.game_over():
                board.play(bots[board.current_player].choose_move(board))
            wins += board.winner() == 1
        self.assertGreaterEqual(wins, 9)


if __name__ == "__main__":
    unittest.main()
