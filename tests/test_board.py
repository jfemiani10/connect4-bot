"""Tests for the Connect Four rules in src/board.py.

Run all tests from the repo root with:
    python3 -m unittest
"""

import unittest

from src.board import Board, COLS, ROWS


def play_all(board, moves):
    """Play a list of columns in order (players alternate automatically)."""
    for col in moves:
        board.play(col)


class TestBoard(unittest.TestCase):
    def test_piece_falls_to_bottom(self):
        board = Board()
        board.play(3)
        self.assertEqual(board.grid[ROWS - 1][3], 1)  # bottom row
        board.play(3)
        self.assertEqual(board.grid[ROWS - 2][3], 2)  # stacks on top

    def test_players_alternate(self):
        board = Board()
        self.assertEqual(board.current_player, 1)
        board.play(0)
        self.assertEqual(board.current_player, 2)

    def test_horizontal_win(self):
        board = Board()
        # Player 1 plays 0,1,2,3 along the bottom; player 2 stacks on top.
        play_all(board, [0, 0, 1, 1, 2, 2, 3])
        self.assertEqual(board.winner(), 1)
        self.assertTrue(board.game_over())

    def test_vertical_win(self):
        board = Board()
        # Player 1 stacks column 0; player 2 stacks column 1.
        play_all(board, [0, 1, 0, 1, 0, 1, 0])
        self.assertEqual(board.winner(), 1)

    def test_diagonal_win_up_right(self):
        board = Board()
        # Builds a / diagonal for player 1 at columns 0,1,2,3.
        play_all(board, [0, 1, 1, 2, 2, 3, 2, 3, 3, 6, 3])
        self.assertEqual(board.winner(), 1)

    def test_diagonal_win_up_left(self):
        board = Board()
        # Mirror of the test above: a \ diagonal at columns 6,5,4,3.
        play_all(board, [6, 5, 5, 4, 4, 3, 4, 3, 3, 0, 3])
        self.assertEqual(board.winner(), 1)

    def test_three_in_a_row_is_not_a_win(self):
        board = Board()
        play_all(board, [0, 0, 1, 1, 2])
        self.assertIsNone(board.winner())
        self.assertFalse(board.game_over())

    def test_full_column_is_not_valid(self):
        board = Board()
        play_all(board, [0] * ROWS)
        self.assertNotIn(0, board.valid_moves())
        with self.assertRaises(ValueError):
            board.play(0)

    def test_draw_when_board_fills(self):
        board = Board()
        # This order fills the board without anyone getting 4 in a row:
        # columns are filled in pairs so colors alternate in a safe pattern.
        order = [0, 1] * 3 + [1, 0] * 3 + [2, 3] * 3 + [3, 2] * 3 + [4, 5] * 3 + [5, 4] * 3 + [6] * 6
        play_all(board, order)
        self.assertTrue(board.is_full())
        self.assertIsNone(board.winner())
        self.assertTrue(board.game_over())

    def test_copy_is_independent(self):
        board = Board()
        board.play(3)
        clone = board.copy()
        clone.play(4)
        self.assertEqual(board.grid[ROWS - 1][4], 0)  # original unchanged
        self.assertEqual(clone.grid[ROWS - 1][4], 2)

    def test_valid_moves_on_empty_board(self):
        self.assertEqual(Board().valid_moves(), list(range(COLS)))


if __name__ == "__main__":
    unittest.main()
