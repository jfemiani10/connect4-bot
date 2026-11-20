"""Plot results from experiments.run_matches CSV files.

Run from the repository root:
    python3 -m experiments.plots

Writes to figures/:
  - minimax vs. the baselines: win rate, positions searched, and seconds per
    move vs. depth
  - MCTS vs. the baselines: win rate and seconds per move vs. iterations
  - minimax vs. MCTS: head_to_head.csv, one row per depth/iterations pairing
Each part is skipped if results/ has no matches of that kind yet.
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path


REQUIRED_FIELDS = {
    "bot1",
    "bot2",
    "depth",
    "alpha_beta",
    "bot1_result",
    "bot2_result",
    "bot1_moves",
    "bot2_moves",
    "bot1_positions_searched",
    "bot2_positions_searched",
    "bot1_seconds_per_move",
    "bot2_seconds_per_move",
}


def _parse_bool(value, field, game):
    normalized = str(value).strip().lower()
    if normalized in ("true", "1"):
        return True
    if normalized in ("false", "0"):
        return False
    raise ValueError(f"Invalid {field} value {value!r} in game {game}")


def read_match_rows(input_dir):
    """Read match-runner CSV files from a directory."""
    csv_paths = sorted(Path(input_dir).glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No match CSV files found in {input_dir}")

    rows = []
    for path in csv_paths:
        with path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            missing = REQUIRED_FIELDS.difference(reader.fieldnames or [])
            if missing:
                raise ValueError(
                    f"{path} is missing required columns: {', '.join(sorted(missing))}"
                )
            for row in reader:
                row["_source"] = str(path)
                rows.append(row)
    if not rows:
        raise ValueError(f"No match records found in CSV files under {input_dir}")
    return rows


def aggregate_match_rows(rows):
    """Aggregate minimax outcomes and per-move metrics by opponent and settings."""
    totals = defaultdict(
        lambda: {
            "games": 0,
            "wins": 0,
            "positions_searched": 0,
            "moves": 0,
            "seconds": 0.0,
        }
    )

    for row in rows:
        if row["bot1"] == "minimax":
            opponent = row["bot2"]
            result = row["bot1_result"]
            slot = "bot1"
        elif row["bot2"] == "minimax":
            opponent = row["bot1"]
            result = row["bot2_result"]
            slot = "bot2"
        else:
            continue

        if opponent not in ("random", "greedy"):
            continue

        game = row.get("game", "?")
        try:
            depth = int(row["depth"])
            moves = int(row[f"{slot}_moves"])
            positions = int(row[f"{slot}_positions_searched"])
            seconds_per_move = float(row[f"{slot}_seconds_per_move"])
            alpha_beta = _parse_bool(row["alpha_beta"], "alpha_beta", game)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid match data in {row.get('_source', 'CSV')} game {game}: {error}"
            ) from error

        if depth < 1 or moves < 1 or positions < 0 or seconds_per_move < 0:
            raise ValueError(
                f"Invalid metric values in {row.get('_source', 'CSV')} game {game}"
            )
        if result not in ("win", "loss", "draw"):
            raise ValueError(f"Invalid minimax result {result!r} in game {game}")

        aggregate = totals[(opponent, depth, alpha_beta)]
        aggregate["games"] += 1
        aggregate["wins"] += result == "win"
        aggregate["positions_searched"] += positions
        aggregate["moves"] += moves
        aggregate["seconds"] += seconds_per_move * moves

    return {
        key: {
            "win_rate": values["wins"] / values["games"],
            "mean_positions_per_move": values["positions_searched"] / values["moves"],
            "mean_seconds_per_move": values["seconds"] / values["moves"],
            "games": values["games"],
        }
        for key, values in totals.items()
    }


def make_plots(aggregates, output_dir):
    """Save win-rate, search-count, and decision-time charts."""
    if not aggregates:
        raise ValueError("No minimax matches against random or greedy were found")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    chart_specs = [
        ("win_rate", "Minimax win rate vs. depth", "Win rate", "win_rate_vs_depth.png"),
        (
            "mean_positions_per_move",
            "Minimax positions searched vs. depth",
            "Mean positions searched per move",
            "positions_searched_vs_depth.png",
        ),
        (
            "mean_seconds_per_move",
            "Minimax decision time vs. depth",
            "Mean seconds per move",
            "time_per_move_vs_depth.png",
        ),
    ]
    output_paths = []
    for metric, title, y_label, filename in chart_specs:
        figure, axis = plt.subplots(figsize=(8, 5))
        series = defaultdict(list)
        for (opponent, depth, alpha_beta), values in aggregates.items():
            series[(opponent, alpha_beta)].append((depth, values[metric]))

        for (opponent, alpha_beta), points in sorted(series.items()):
            # Pruning never changes minimax's moves, so its win rate is the
            # same either way. The no-pruning runs use fewer games, which
            # would make a different-looking (but not different) win rate,
            # so they're left off the win-rate chart.
            if metric == "win_rate" and not alpha_beta:
                continue
            points.sort()
            pruning_label = "alpha-beta" if alpha_beta else "no pruning"
            axis.plot(
                [point[0] for point in points],
                [point[1] for point in points],
                marker="o",
                label=f"vs {opponent} ({pruning_label})",
            )

        axis.set_title(title)
        axis.set_xlabel("Minimax search depth")
        axis.set_ylabel(y_label)
        axis.set_xticks(sorted({depth for _, depth, _ in aggregates}))
        axis.grid(True, alpha=0.3)
        axis.legend()
        if metric == "win_rate":
            axis.set_ylim(0, 1)
            axis.yaxis.set_major_formatter(PercentFormatter(1.0))
        else:
            # Search cost grows exponentially with depth, so a log scale
            # keeps the small pruned values visible next to the large ones.
            axis.set_yscale("log")
            axis.set_ylabel(f"{y_label} (log scale)")
        figure.tight_layout()
        output_path = output_dir / filename
        figure.savefig(output_path, dpi=160)
        plt.close(figure)
        output_paths.append(output_path)

    return output_paths


BASELINES = ("random", "greedy")


def _slot_of(row, bot_name):
    """Return "bot1" or "bot2" for whichever side of the row is `bot_name`, else None."""
    if row["bot1"] == bot_name:
        return "bot1"
    if row["bot2"] == bot_name:
        return "bot2"
    return None


def _other(slot):
    return "bot2" if slot == "bot1" else "bot1"


def aggregate_mcts_rows(rows):
    """Aggregate MCTS outcomes against the baselines by opponent and iterations.

    Returns {(opponent, iterations): {"win_rate", "mean_seconds_per_move", "games"}}.
    """
    totals = defaultdict(lambda: {"games": 0, "wins": 0, "moves": 0, "seconds": 0.0})

    for row in rows:
        slot = _slot_of(row, "mcts")
        if slot is None:
            continue
        opponent = row[_other(slot)]
        if opponent not in BASELINES:
            continue

        moves = int(row[f"{slot}_moves"])
        aggregate = totals[(opponent, int(row["iterations"]))]
        aggregate["games"] += 1
        aggregate["wins"] += row[f"{slot}_result"] == "win"
        aggregate["moves"] += moves
        aggregate["seconds"] += float(row[f"{slot}_seconds_per_move"]) * moves

    return {
        key: {
            "win_rate": values["wins"] / values["games"],
            "mean_seconds_per_move": values["seconds"] / values["moves"],
            "games": values["games"],
        }
        for key, values in totals.items()
    }


def make_mcts_plots(aggregates, output_dir):
    """Save MCTS win-rate and decision-time charts against iterations per move."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    chart_specs = [
        ("win_rate", "MCTS win rate vs. iterations", "Win rate", "win_rate_vs_iterations.png"),
        (
            "mean_seconds_per_move",
            "MCTS decision time vs. iterations",
            "Mean seconds per move",
            "time_per_move_vs_iterations.png",
        ),
    ]
    iteration_counts = sorted({iterations for _, iterations in aggregates})
    output_paths = []
    for metric, title, y_label, filename in chart_specs:
        figure, axis = plt.subplots(figsize=(8, 5))
        series = defaultdict(list)
        for (opponent, iterations), values in aggregates.items():
            series[opponent].append((iterations, values[metric]))

        for opponent, points in sorted(series.items()):
            points.sort()
            axis.plot(
                [point[0] for point in points],
                [point[1] for point in points],
                marker="o",
                label=f"vs {opponent}",
            )

        axis.set_title(title)
        axis.set_xlabel("MCTS iterations per move (log scale)")
        axis.set_ylabel(y_label)
        # Iteration counts span 100 to 5000, so a log scale spaces them evenly.
        axis.set_xscale("log")
        axis.set_xticks(iteration_counts)
        axis.set_xticklabels([str(count) for count in iteration_counts])
        axis.grid(True, alpha=0.3)
        axis.legend()
        if metric == "win_rate":
            axis.set_ylim(0, 1)
            axis.yaxis.set_major_formatter(PercentFormatter(1.0))
        figure.tight_layout()
        output_path = output_dir / filename
        figure.savefig(output_path, dpi=160)
        plt.close(figure)
        output_paths.append(output_path)

    return output_paths


HEAD_TO_HEAD_FIELDS = [
    "minimax_depth",
    "minimax_alpha_beta",
    "mcts_iterations",
    "games",
    "minimax_win_rate",
    "draw_rate",
    "mcts_win_rate",
    "minimax_seconds_per_move",
    "mcts_seconds_per_move",
]


def aggregate_head_to_head(rows):
    """Summarize minimax vs. MCTS games, one entry per depth/iterations pairing."""
    totals = defaultdict(
        lambda: {
            "games": 0, "minimax_wins": 0, "draws": 0, "mcts_wins": 0,
            "minimax_moves": 0, "minimax_seconds": 0.0,
            "mcts_moves": 0, "mcts_seconds": 0.0,
        }
    )

    for row in rows:
        minimax_slot = _slot_of(row, "minimax")
        mcts_slot = _slot_of(row, "mcts")
        if minimax_slot is None or mcts_slot is None:
            continue

        key = (int(row["depth"]), _parse_bool(row["alpha_beta"], "alpha_beta", row.get("game", "?")),
               int(row["iterations"]))
        aggregate = totals[key]
        aggregate["games"] += 1
        result = row[f"{minimax_slot}_result"]
        if result == "win":
            aggregate["minimax_wins"] += 1
        elif result == "loss":
            aggregate["mcts_wins"] += 1
        else:
            aggregate["draws"] += 1
        for name, slot in (("minimax", minimax_slot), ("mcts", mcts_slot)):
            moves = int(row[f"{slot}_moves"])
            aggregate[f"{name}_moves"] += moves
            aggregate[f"{name}_seconds"] += float(row[f"{slot}_seconds_per_move"]) * moves

    summary = []
    for (depth, alpha_beta, iterations), values in sorted(totals.items()):
        games = values["games"]
        summary.append({
            "minimax_depth": depth,
            "minimax_alpha_beta": alpha_beta,
            "mcts_iterations": iterations,
            "games": games,
            "minimax_win_rate": values["minimax_wins"] / games,
            "draw_rate": values["draws"] / games,
            "mcts_win_rate": values["mcts_wins"] / games,
            "minimax_seconds_per_move": values["minimax_seconds"] / max(values["minimax_moves"], 1),
            "mcts_seconds_per_move": values["mcts_seconds"] / max(values["mcts_moves"], 1),
        })
    return summary


def write_head_to_head(summary, output_dir):
    """Save the head-to-head summary as a CSV table (Table II in the paper)."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "head_to_head.csv"
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=HEAD_TO_HEAD_FIELDS)
        writer.writeheader()
        writer.writerows(summary)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Plot minimax results from CSV files written by experiments.run_matches."
    )
    parser.add_argument("--input-dir", default="results", help="directory containing match CSV files")
    parser.add_argument("--output-dir", default="figures", help="directory for generated PNG figures")
    args = parser.parse_args()

    try:
        rows = read_match_rows(args.input_dir)
        output_paths = []

        minimax_aggregates = aggregate_match_rows(rows)
        if minimax_aggregates:
            output_paths += make_plots(minimax_aggregates, args.output_dir)

        mcts_aggregates = aggregate_mcts_rows(rows)
        if mcts_aggregates:
            output_paths += make_mcts_plots(mcts_aggregates, args.output_dir)

        head_to_head = aggregate_head_to_head(rows)
        if head_to_head:
            output_paths.append(write_head_to_head(head_to_head, args.output_dir))

        if not output_paths:
            raise ValueError("No minimax or MCTS matches found to plot")
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))

    for output_path in output_paths:
        print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
