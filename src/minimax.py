"""Minimax bot with optional alpha-beta pruning.

HOW MINIMAX WORKS
-----------------
To pick a move, the bot imagines every move it could make, then every reply
the opponent could make, then every reply to that, and so on, up to `depth`
moves ahead. This forms a "game tree". It then scores the positions at the
bottom of the tree and works back up:

On the bot's own turns it assumes it will pick the HIGHEST-scoring move
(the "max" player).
On the opponent's turns it assumes the opponent picks the move that is
LOWEST-scoring for the bot (the "min" player), i.e. the opponent plays well.

The move at the top with the best guaranteed score is the one it plays.
Positions at the bottom of the tree are usually not finished games, so we
guess how good they are with a heuristic, `evaluate()`, below.

HOW ALPHA-BETA PRUNING WORKS
----------------------------
Alpha-beta gives the exact same answer as plain minimax, but skips branches
that can't change the decision. While searching, it tracks two numbers:

  alpha = the best score the max player (the bot) is already guaranteed
          somewhere else in the tree
  beta  = the best score the min player (the opponent) is already guaranteed
          somewhere else in the tree

If a branch is ever found to be worse than an option a player already has
(alpha >= beta), the rest of that branch is skipped ("pruned"), because a
sensible player would never let the game go down it.

Example: the bot has already found a move that guarantees a score of 5. It
starts checking another move and finds that the opponent has a reply leading
to a score of 2. It doesn't need to look at the opponent's other replies to
that move: the opponent can already hold the bot to 2 or less, which is worse
than the 5 the bot already has, so the bot will never pick that move.

`positions_searched` counts how many positions were looked at, so we can
measure how much pruning saves in the experiments.
"""

import math

from src.board import COLS, CONNECT, ROWS

# Score for a won game. It's far bigger than any heuristic score, so a
# guaranteed win always beats any unfinished position.
WIN_SCORE = 1_000_000

# Columns ordered from the center outwards: 3, 2, 4, 1, 5, 0, 6.
# Center moves are usually best in Connect Four, so trying them first lets
# alpha-beta find good scores early and prune more. It also breaks ties
# toward the center.
MOVE_ORDER = sorted(range(COLS), key=lambda col: abs(col - COLS // 2))


def _all_windows():
    """List every group of 4 cells in a line: every possible way to win.

    Each window is a list of 4 (row, col) cells. There are 69 of them on a
    6 x 7 board. We work them out once, when the program starts, so
    evaluate() doesn't have to.
    """
    windows = []
    for row in range(ROWS):
        for col in range(COLS):
            for d_row, d_col in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                cells = [(row + i * d_row, col + i * d_col) for i in range(CONNECT)]
                # Keep the window only if all 4 cells are on the board.
                if all(0 <= r < ROWS and 0 <= c < COLS for r, c in cells):
                    windows.append(cells)
    return windows


WINDOWS = _all_windows()


def evaluate(board, me):
    """Heuristic score of an unfinished position, from player `me`'s view.

    Positive means good for `me`, negative means good for the opponent.
    It looks at every window of 4 cells:
      - 3 of my pieces + 1 empty cell:  +5  (one move from winning)
      - 2 of my pieces + 2 empty cells: +2  (could grow into a win)
      - the same patterns for the opponent count against me (-5, -2)
    Windows containing pieces from BOTH players can never become a win for
    either player, so they score 0.
    Each of my pieces in the center column adds +3 (and each of the
    opponent's subtracts 3), because the center is part of the most possible
    lines of 4.

    The score is "zero-sum": evaluate(board, 1) == -evaluate(board, 2).
    """
    opponent = 3 - me
    score = 0

    for window in WINDOWS:
        cells = [board.grid[r][c] for r, c in window]
        mine = cells.count(me)
        theirs = cells.count(opponent)
        empty = cells.count(0)

        if theirs == 0:
            if mine == 3 and empty == 1:
                score += 5
            elif mine == 2 and empty == 2:
                score += 2
        elif mine == 0:
            if theirs == 3 and empty == 1:
                score -= 5
            elif theirs == 2 and empty == 2:
                score -= 2

    center = COLS // 2
    for row in range(ROWS):
        if board.grid[row][center] == me:
            score += 3
        elif board.grid[row][center] == opponent:
            score -= 3

    return score


class MinimaxBot:
    """Looks `depth` moves ahead with minimax and picks the best move.

    depth:      how many moves (the bot's and the opponent's) to look ahead.
                Higher is stronger but much slower.
    alpha_beta: True to use alpha-beta pruning. Either way, the bot picks
                the same moves; pruning just searches fewer positions.
    """

    def __init__(self, depth=4, alpha_beta=True):
        self.depth = depth
        self.alpha_beta = alpha_beta
        self.name = f"minimax (depth {depth}{'' if alpha_beta else ', no pruning'})"
        self.positions_searched = 0  # for the most recent move only

    def choose_move(self, board):
        self.positions_searched = 0
        me = board.current_player  # the player we're choosing a move for

        best_score = -math.inf
        best_move = None
        alpha, beta = -math.inf, math.inf

        # Top level of the tree: try each of our moves on a copy of the board
        # and see what score minimax gives the resulting position.
        for col in self._ordered_moves(board):
            child = board.copy()
            child.play(col)
            # After our move it's the opponent's turn, so they are the
            # minimizing player at the next level down.
            score = self._minimax(child, self.depth - 1, alpha, beta, False, me)

            # Strictly greater: when two moves tie, keep the earlier one,
            # which is the one closer to the center.
            if score > best_score:
                best_score = score
                best_move = col
            if self.alpha_beta:
                alpha = max(alpha, best_score)

        return best_move

    def _minimax(self, board, depth, alpha, beta, maximizing, me):
        """Return the minimax score of `board` from player `me`'s point of view.

        depth:      how many more moves to look ahead from here.
        alpha/beta: the bounds described at the top of this file.
        maximizing: True if it's `me`'s turn (pick the highest score),
                    False if it's the opponent's turn (pick the lowest).
        """
        self.positions_searched += 1

        #Stop searching if the game is over or we've hit the depth limit.
        winner = board.winner()
        if winner == me:
            # Adding `depth` makes faster wins score higher: a win found with
            # more depth left over happened sooner, so the bot goes for the
            # quickest win instead of wandering around.
            return WIN_SCORE + depth
        if winner is not None:
            # Likewise, a loss further away scores less badly, so a bot that
            # can't avoid losing at least makes it take as long as possible.
            return -(WIN_SCORE + depth)
        if board.is_full():
            return 0  # draw
        if depth == 0:
            return evaluate(board, me)

        # Otherwise, try every move and pass the result back up.
        if maximizing:
            # Our turn: we pick the move with the highest score.
            best = -math.inf
            for col in self._ordered_moves(board):
                child = board.copy()
                child.play(col)
                best = max(best, self._minimax(child, depth - 1, alpha, beta, False, me))
                if self.alpha_beta:
                    alpha = max(alpha, best)
                    if alpha >= beta:
                        # The opponent already has a way to avoid this
                        # position that's at least as good for them, so they'd
                        # never let the game get here. Skip the other moves.
                        break
            return best
        else:
            # Opponent's turn: assume they pick the lowest score for us.
            best = math.inf
            for col in self._ordered_moves(board):
                child = board.copy()
                child.play(col)
                best = min(best, self._minimax(child, depth - 1, alpha, beta, True, me))
                if self.alpha_beta:
                    beta = min(beta, best)
                    if alpha >= beta:
                        # We already have a better option elsewhere, so we'd
                        # never let the game get here. Skip the other moves.
                        break
            return best

    @staticmethod
    def _ordered_moves(board):
        """Legal moves, center columns first (see MOVE_ORDER)."""
        valid = board.valid_moves()
        return [col for col in MOVE_ORDER if col in valid]
