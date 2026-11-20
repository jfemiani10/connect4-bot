"""Run every experiment in the paper, then make all the figures.

Run from the repository root:
    python3 -m experiments.run_all               # full run, one matchup at a time (~40 min)
    python3 -m experiments.run_all --workers 6   # full run, 6 matchups at once (~10 min)
    python3 -m experiments.run_all --games 2     # a quick smoke test

Each matchup is saved to its own CSV in results/ (overwriting any old copy),
then experiments.plots turns them into figures/. The machine's specs are
saved to results/environment.txt for the paper's Hardware section.

By default, matchups run one at a time, so the time-per-move numbers aren't
slowed down by other matchups competing for the CPU. --workers N runs N
matchups at once in separate processes (Python threads can't run Python code
in parallel). Win rates are identical either way, because every game is
seeded; only the timings get noisier, and the worker count is saved in
environment.txt so the paper can report it.
"""

import argparse
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import platform
import subprocess
import sys
import time

from experiments.run_matches import run_matches

SEED = 42
GAMES = 100

# Minimax picks exactly the same moves with or without pruning, so the
# no-pruning runs only measure the cost of searching. A few games are enough
# for that, and depth 6 without pruning takes about 2 seconds per move.
NO_PRUNING_GAMES = 20

MINIMAX_DEPTHS = [1, 2, 3, 4, 5, 6]
MCTS_ITERATIONS = [100, 300, 1000, 3000, 5000]
HEAD_TO_HEAD_DEPTHS = [2, 4, 6]
HEAD_TO_HEAD_ITERATIONS = [100, 1000, 5000]
BASELINES = ["random", "greedy"]


def build_plan(games=GAMES, no_pruning_games=NO_PRUNING_GAMES):
    """List every matchup as (output filename, keyword arguments for run_matches)."""
    plan = []

    # 1. Minimax vs. each baseline, at every depth, with and without pruning.
    for depth in MINIMAX_DEPTHS:
        for opponent in BASELINES:
            plan.append((f"minimax_d{depth}_vs_{opponent}.csv", dict(
                bot1_name="minimax", bot2_name=opponent, games=games, depth=depth)))
            plan.append((f"minimax_d{depth}_nopruning_vs_{opponent}.csv", dict(
                bot1_name="minimax", bot2_name=opponent, games=no_pruning_games,
                depth=depth, alpha_beta=False)))

    # 2. MCTS vs. each baseline, at every iteration count.
    for iterations in MCTS_ITERATIONS:
        for opponent in BASELINES:
            plan.append((f"mcts_{iterations}_vs_{opponent}.csv", dict(
                bot1_name="mcts", bot2_name=opponent, games=games, iterations=iterations)))

    # 3. Minimax vs. MCTS head to head.
    for depth in HEAD_TO_HEAD_DEPTHS:
        for iterations in HEAD_TO_HEAD_ITERATIONS:
            plan.append((f"minimax_d{depth}_vs_mcts_{iterations}.csv", dict(
                bot1_name="minimax", bot2_name="mcts", games=games,
                depth=depth, iterations=iterations)))

    # 4. Sanity check: the greedy baseline should beat the random one.
    plan.append(("greedy_vs_random.csv", dict(
        bot1_name="greedy", bot2_name="random", games=games)))

    return plan


def _cpu_name():
    """CPU model name from /proc/cpuinfo on Linux, else what Python reports."""
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as cpuinfo:
            for line in cpuinfo:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def write_environment(path, total_seconds, workers):
    """Save the machine details the paper's Hardware section asks for."""
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "unknown"
    with open(path, "w", encoding="utf-8") as env_file:
        env_file.write(f"CPU: {_cpu_name()}\n")
        env_file.write(f"Logical cores: {os.cpu_count()}\n")
        env_file.write(f"OS: {platform.platform()}\n")
        env_file.write(f"Python: {platform.python_version()}\n")
        env_file.write(f"Git commit: {commit}\n")
        env_file.write(f"Matchups run in parallel: {workers}\n")
        env_file.write(f"Total run time: {total_seconds / 60:.1f} minutes\n")


def run_one(filename, kwargs, results_dir):
    """Run one matchup and save its CSV. Returns a one-line progress summary.

    This is a top-level function so worker processes can call it.
    """
    start = time.perf_counter()
    rows, _ = run_matches(seed=SEED, output_path=os.path.join(results_dir, filename), **kwargs)
    bot1_wins = sum(row["bot1_result"] == "win" for row in rows)
    return (f"{filename}: bot1 won {bot1_wins}/{len(rows)} "
            f"({time.perf_counter() - start:.0f}s)")


def main():
    parser = argparse.ArgumentParser(description="Run every experiment, then make all figures.")
    parser.add_argument("--games", type=int, default=GAMES,
                        help=f"games per matchup (default {GAMES})")
    parser.add_argument("--no-pruning-games", type=int, default=NO_PRUNING_GAMES,
                        help=f"games per no-pruning matchup (default {NO_PRUNING_GAMES})")
    parser.add_argument("--workers", type=int, default=1,
                        help="matchups to run at once (default 1: one at a time, cleanest timings)")
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--figures-dir", default="figures")
    args = parser.parse_args()

    plan = build_plan(args.games, min(args.no_pruning_games, args.games))
    start = time.perf_counter()

    if args.workers <= 1:
        for number, (filename, kwargs) in enumerate(plan, start=1):
            print(f"[{number}/{len(plan)}] {run_one(filename, kwargs, args.results_dir)}", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(run_one, filename, kwargs, args.results_dir)
                       for filename, kwargs in plan]
            # Print each matchup as it finishes, which may be out of order.
            for number, future in enumerate(as_completed(futures), start=1):
                print(f"[{number}/{len(plan)}] {future.result()}", flush=True)

    write_environment(os.path.join(args.results_dir, "environment.txt"),
                      time.perf_counter() - start, args.workers)

    # Make the figures with the same Python interpreter that ran the matches.
    subprocess.run([sys.executable, "-m", "experiments.plots",
                    "--input-dir", args.results_dir, "--output-dir", args.figures_dir],
                   check=True)


if __name__ == "__main__":
    main()
