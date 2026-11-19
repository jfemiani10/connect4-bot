"""Baseline bots that the minimax bot is compared against.

Every bot in this project follows the same simple interface:
    bot.name                -> a short label used in printouts and results files
    bot.choose_move(board)  -> returns the column (0-6) the bot wants to play

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

    def choose_move(self, board):
        return self.rng.choice(board.valid_moves())


# TODO (Ryan): add GreedyBot here, following the same interface:
#   1. If a move wins immediately, play it.
#   2. Otherwise, if the opponent could win next turn in some column, block it.
#   3. Otherwise, play a random legal column.
