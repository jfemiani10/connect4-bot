"""Run reproducible Connect Four bot matches and save per-game metrics.

Run from the repository root, for example:
    python3 -m experiments.run_matches --bot1 minimax --bot2 greedy --games 100
"""

import argparse
import csv
import os
import random
import time
from datetime import datetime

from src.baselines import GreedyBot, RandomBot
from src.board import Board
from src.minimax import MinimaxBot


CSV_FIELDS = [
    "game",
    "seed",
    "bot1",
    "bot2",
    "bot1_player",
    "bot2_player",
    "winner",
    "bot1_result",
    "bot2_result",
    "moves",
    "depth",
    "alpha_beta",
    "bot1_moves",
    "bot2_moves",
    "bot1_positions_searched",
    "bot2_positions_searched",
    "bot1_seconds_per_move",
    "bot2_seconds_per_move",
]


def _create_bot(name, seed, depth, alpha_beta):
    """Create one bot with the requested repeatable random seed."""
    if name == "random":
        return RandomBot(seed=seed)
    if name == "greedy":
        return GreedyBot(seed=seed)
    if name == "minimax":
        return MinimaxBot(depth=depth, alpha_beta=alpha_beta)
    raise ValueError(f"Unknown bot: {name}")


def play_game(bot1_name, bot2_name, game_number, seed, depth=4, alpha_beta=True):
    """Play one game and return its result and per-bot performance metrics."""
    game_seed = seed + game_number - 1
    bot1_rng = random.Random(game_seed * 2)
    bot2_rng = random.Random(game_seed * 2 + 1)
    bots = {
        1: _create_bot(bot1_name, bot1_rng.randrange(2 ** 32), depth, alpha_beta),
        2: _create_bot(bot2_name, bot2_rng.randrange(2 ** 32), depth, alpha_beta),
    }

    bot1_player = 1 if game_number % 2 == 1 else 2
    bot2_player = 3 - bot1_player
    board = Board()
    elapsed = {"bot1": 0.0, "bot2": 0.0}
    positions = {"bot1": 0, "bot2": 0}
    move_counts = {"bot1": 0, "bot2": 0}
    bot_slots = {bot1_player: "bot1", bot2_player: "bot2"}

    while not board.game_over():
        player = board.current_player
        bot_slot = bot_slots[player]
        bot = bots[player]
        start = time.perf_counter()
        move = bot.choose_move(board)
        elapsed[bot_slot] += time.perf_counter() - start
        positions[bot_slot] += getattr(bot, "positions_searched", 0)
        move_counts[bot_slot] += 1
        board.play(move)

    winner = board.winner()
    if winner is None:
        bot1_result = bot2_result = "draw"
        winner_name = "draw"
    else:
        winner_name = bot_slots[winner]
        bot1_result = "win" if winner == bot1_player else "loss"
        bot2_result = "win" if winner == bot2_player else "loss"

    return {
        "game": game_number,
        "seed": game_seed,
        "bot1": bot1_name,
        "bot2": bot2_name,
        "bot1_player": bot1_player,
        "bot2_player": bot2_player,
        "winner": winner_name,
        "bot1_result": bot1_result,
        "bot2_result": bot2_result,
        "moves": move_counts["bot1"] + move_counts["bot2"],
        "depth": depth,
        "alpha_beta": alpha_beta,
        "bot1_moves": move_counts["bot1"],
        "bot2_moves": move_counts["bot2"],
        "bot1_positions_searched": positions["bot1"],
        "bot2_positions_searched": positions["bot2"],
        "bot1_seconds_per_move": (
            elapsed["bot1"] / move_counts["bot1"] if move_counts["bot1"] else 0.0
        ),
        "bot2_seconds_per_move": (
            elapsed["bot2"] / move_counts["bot2"] if move_counts["bot2"] else 0.0
        ),
    }


def run_matches(bot1_name, bot2_name, games, seed=0, depth=4, alpha_beta=True, output_path=None):
    """Play `games` alternating-start matches and write per-game CSV results."""
    if games < 1:
        raise ValueError("games must be at least 1")
    if depth < 1:
        raise ValueError("depth must be at least 1")
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = os.path.join("results", f"matches_{timestamp}.csv")

    rows = [
        play_game(bot1_name, bot2_name, game, seed, depth, alpha_beta)
        for game in range(1, games + 1)
    ]

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    return rows, output_path


def main():
    parser = argparse.ArgumentParser(description="Run Connect Four bot matches and save CSV metrics.")
    parser.add_argument("--bot1", choices=("random", "greedy", "minimax"), default="minimax")
    parser.add_argument("--bot2", choices=("random", "greedy", "minimax"), default="random")
    parser.add_argument("--games", type=int, default=100, help="number of games to play")
    parser.add_argument("--depth", type=int, default=4, help="minimax search depth")
    parser.add_argument("--no-pruning", action="store_true", help="disable minimax alpha-beta pruning")
    parser.add_argument("--seed", type=int, default=0, help="base seed for repeatable bot moves")
    parser.add_argument("--output", help="CSV output path (default: results/matches_<timestamp>.csv)")
    args = parser.parse_args()

    if args.games < 1:
        parser.error("--games must be at least 1")
    if args.depth < 1:
        parser.error("--depth must be at least 1")

    rows, output_path = run_matches(
        args.bot1,
        args.bot2,
        args.games,
        seed=args.seed,
        depth=args.depth,
        alpha_beta=not args.no_pruning,
        output_path=args.output,
    )

    bot1_results = {"win": 0, "loss": 0, "draw": 0}
    bot2_results = {"win": 0, "loss": 0, "draw": 0}
    for row in rows:
        bot1_results[row["bot1_result"]] += 1
        bot2_results[row["bot2_result"]] += 1
    print(f"Played {len(rows)} games: {args.bot1} vs {args.bot2}")
    print(f"bot1 ({args.bot1}): {bot1_results}")
    print(f"bot2 ({args.bot2}): {bot2_results}")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
