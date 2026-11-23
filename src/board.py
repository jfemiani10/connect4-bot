"""Connect Four board: game state and rules.
The board is a 6 x 7 grid stored as a list of rows, with row 0 at the TOP.
Each cell holds:
0 = empty
1 = player 1's piece (goes first, shown in red)
2 = player 2's piece (shown in yellow)

Pieces "fall" to the lowest empty row of the chosen column, just like the
real game. A player wins by getting 4 of their pieces in a row horizontally,
vertically, or diagonally. If the board fills up with no winner, it's a draw.
"""

ROWS = 6
COLS = 7
CONNECT = 4 # how many in a row are needed to win, just good practice not to hardcode
# (Allow for testing with larger boards in future?)

# The four directions a line of 4 can run, as (row step, column step).
# We only need four since each line is checked forwards and backwards.
DIRECTIONS = [
    (0, 1), # horizontal
    (1, 0), # vertical
    (1, 1), # diagonal
    (1, -1), # diagonal
]


class Board:
    def __init__(self):
        # Start with every cell empty.
        self.grid = [[0] * COLS for _ in range(ROWS)]
        self.current_player = 1   # player 1 always moves first
        self.last_move = None # column of the most recent move (for display)
        self._winner = None # set to 1 or 2 once someone connects four
        self._moves_played = 0 # used to detect a full board quickly

    def valid_moves(self):
        """Return the list of columns that still have room for a piece.

        A column has room if its TOP cell (row 0) is still empty.
        """
        return [col for col in range(COLS) if self.grid[0][col] == 0]

    def play(self, col):
        """Drop the current player's piece into `col`, then switch turns.

        Raises ValueError if the column is out of range, full, or the game
        is already over.
        """
        if self.game_over():
            raise ValueError("The game is already over.")
        if col not in self.valid_moves():
            raise ValueError(f"Column {col} is not a valid move.")

        # Find the lowest empty row in this column by scanning from the bottom up.
        for row in range(ROWS - 1, -1, -1):
            if self.grid[row][col] == 0:
                self.grid[row][col] = self.current_player
                break

        self.last_move = col
        self._moves_played += 1

        # A new piece can only create a win that includes that piece,
        # so we only need to check lines running through (row, col).
        if self._connects_four(row, col):
            self._winner = self.current_player

        # Hand the turn to the other player (1 -> 2, 2 -> 1).
        self.current_player = 3 - self.current_player

    def winner(self):
        """Return 1 or 2 if that player has won, or None if nobody has (yet)."""
        return self._winner

    def is_full(self):
        """Return True if every cell is filled."""
        return self._moves_played == ROWS * COLS

    def game_over(self):
        """The game ends when someone wins or the board is full (a draw)."""
        return self._winner is not None or self.is_full()

    def copy(self):
        """Return an independent copy of this board.

        Bots use this to try out moves without changing the real game.
        """
        new = Board()
        new.grid = [row[:] for row in self.grid]  # copy each row, not just the outer list
        new.current_player = self.current_player
        new.last_move = self.last_move
        new._winner = self._winner
        new._moves_played = self._moves_played
        return new

    def _connects_four(self, row, col):
        """Return True if the piece at (row, col) is part of 4 in a row."""
        player = self.grid[row][col]
        for d_row, d_col in DIRECTIONS:
            # Count the piece itself, then walk outwards in both directions
            # along this line while the cells belong to the same player.
            count = 1
            count += self._count_in_direction(row, col, d_row, d_col, player)
            count += self._count_in_direction(row, col, -d_row, -d_col, player)
            if count >= CONNECT:
                return True
        return False

    def _count_in_direction(self, row, col, d_row, d_col, player):
        """Count `player`'s pieces in a line from (row, col), not including it."""
        count = 0
        r, c = row + d_row, col + d_col
        while 0 <= r < ROWS and 0 <= c < COLS and self.grid[r][c] == player:
            count += 1
            r += d_row
            c += d_col
        return count
