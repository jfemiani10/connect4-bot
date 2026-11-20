"""Play Connect Four against a bot in the terminal.

Run from the repo root:
    python3 play.py                          # play the random bot, you go first
    python3 play.py --bot minimax            # play minimax (looks 4 moves ahead)
    python3 play.py --bot minimax --depth 6  # a stronger, slower minimax
    python3 play.py --bot mcts               # play Monte Carlo Tree Search (1000 iterations)
    python3 play.py --bot mcts --iterations 5000  # a stronger, slower MCTS
    python3 play.py --second                 # the bot goes first
    python3 play.py --seed 42                # make the random and MCTS bots repeatable

Type a column number (0-6) to drop your piece, or q to quit.
"""

import argparse

from src.baselines import RandomBot
from src.board import Board
from src.display import print_board
from src.mcts import MCTSBot
from src.minimax import MinimaxBot

# Player 1 is always shown in red and player 2 in yellow (see src/display.py).
COLOR_NAMES = {1: "red", 2: "yellow"}

# The bots you can pick with --bot. Each entry builds a bot from the
# command-line options. To add a new bot (e.g. greedy), add a line here.
BOTS = {
    "random": lambda args: RandomBot(seed=args.seed),
    "minimax": lambda args: MinimaxBot(depth=args.depth, alpha_beta=not args.no_pruning),
    "mcts": lambda args: MCTSBot(iterations=args.iterations, seed=args.seed),
}


def ask_human_for_move(board):
    """Keep asking until the human types a valid column. Returns None to quit."""
    valid = board.valid_moves()
    while True:
        text = input(f"Your move {valid} (q to quit): ").strip().lower()
        if text in ("q", "quit", "exit"):
            return None
        if text.isdigit() and int(text) in valid:
            return int(text)
        print("  That's not a valid column, try again.")


def main():
    parser = argparse.ArgumentParser(description="Play Connect Four against a bot.")
    parser.add_argument("--bot", choices=BOTS, default="random", help="which bot to play")
    parser.add_argument("--depth", type=int, default=4, help="minimax: moves to look ahead")
    parser.add_argument("--no-pruning", action="store_true",
                        help="minimax: turn off alpha-beta pruning (same moves, slower)")
    parser.add_argument("--iterations", type=int, default=1000,
                        help="mcts: simulations to run per move")
    parser.add_argument("--second", action="store_true", help="let the bot move first")
    parser.add_argument("--seed", type=int, default=None, help="random seed for the random and MCTS bots")
    args = parser.parse_args()

    # Build the chosen bot. All bots share the same choose_move(board)
    # interface, so the game loop below works with any of them.
    bot = BOTS[args.bot](args)

    human = 2 if args.second else 1  # player number the human controls
    board = Board()

    print(f"You are {COLOR_NAMES[human]}. The {bot.name} bot is {COLOR_NAMES[3 - human]}.\n")
    print_board(board.grid)

    # Main game loop: one iteration per move, until someone wins or the board fills.
    while not board.game_over():
        if board.current_player == human:
            col = ask_human_for_move(board)
            if col is None:
                print("Bye!")
                return
        else:
            col = bot.choose_move(board)
            print(f"The {bot.name} bot plays column {col}.")
            # Only the minimax bot counts positions searched, so check first.
            if hasattr(bot, "positions_searched"):
                print(f"  (searched {bot.positions_searched:,} positions)")

        board.play(col)
        print_board(board.grid, last_move=col)

    # Report the result.
    if board.winner() == human:
        print("You win!")
    elif board.winner() is not None:
        print(f"The {bot.name} bot wins.")
    else:
        print("It's a draw.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or Ctrl+D: exit quietly instead of printing a traceback.
        print("\nBye!")
