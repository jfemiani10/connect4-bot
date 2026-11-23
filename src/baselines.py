"""Baseline bots that the minimax bot is compared against.
Every bot in this project follows the same simple interface:
bot.name = a short label used in printouts and results files
bot.choose_move(board) = returns the column (0-6) the bot wants to play

choose_move must NOT change the board it's given. If a bot wants to try
moves out, it should work on board.copy() instead.
"""

import random


class RandomBot:
    """Plays a random legal column every turn.

    This is the weakest possible opponent, so any real AI should beat it
    almost every time. That makes it a useful sanity check.
    """

    name = "random"

    def __init__(self, seed=None):
        # Each bot gets its own random number generator. Passing the same seed
        # makes the bot play the exact same moves again, so experiments can be
        # repeated and give identical results.
        self.rng = random.Random(seed)

    # Literally just returns a random move
    def choose_move(self, board):
        return self.rng.choice(board.valid_moves())


class GreedyBot:
    """Win immediately, block an immediate opponent win, or play randomly."""

    name = "greedy"

    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    # Prioritize Winning moves, then blocking moves, otherwise just move random
    def choose_move(self, board):
        valid_moves = board.valid_moves()
        me = board.current_player
        opponent = 3 - me

        winning_moves = []
        for col in valid_moves:
            child = board.copy()
            child.play(col)
            if child.winner() == me:
                winning_moves.append(col)
        if winning_moves:
            return self.rng.choice(winning_moves)

        blocking_moves = []
        for col in valid_moves:
            child = board.copy()
            child.current_player = opponent
            child.play(col)
            if child.winner() == opponent:
                blocking_moves.append(col)
        if blocking_moves:
            return self.rng.choice(blocking_moves)

        return self.rng.choice(valid_moves)
