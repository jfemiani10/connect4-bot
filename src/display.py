"""Print a Connect Four board in the terminal.
The grid is a list of 6 rows of 7 ints, with row 0 at the top:
0 = empty, 1 = player 1 (red), 2 = player 2 (yellow).
"""

import os
import sys

RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _use_color():
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def render(grid, last_move=None):
    """Return the board as a string. last_move (a column index) is marked with a ^."""
    color = _use_color()
    pieces = {
        0: ".",
        1: f"{RED}O{RESET}" if color else "X",
        2: f"{YELLOW}O{RESET}" if color else "O",
    }
    cols = len(grid[0])
    lines = [" ".join(pieces[cell] for cell in row) for row in grid]
    lines.append(" ".join(str(c) for c in range(cols)))
    if last_move is not None:
        lines.append("  " * last_move + "^")
    return "\n".join(lines)


def print_board(grid, last_move=None):
    print(render(grid, last_move))
    print()


if __name__ == "__main__":
    # Demo: python3 src/display.py
    demo = [[0] * 7 for _ in range(6)]
    demo[5][3] = 1
    demo[5][4] = 2
    demo[4][3] = 1
    demo[5][2] = 2
    print_board(demo, last_move=2)
