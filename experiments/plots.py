"""Plot results from experiments.run_matches CSV files.

Run from the repository root:
    python3 -m experiments.plots
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
        figure.tight_layout()
        output_path = output_dir / filename
        figure.savefig(output_path, dpi=160)
        plt.close(figure)
        output_paths.append(output_path)

    return output_paths


def main():
    parser = argparse.ArgumentParser(
        description="Plot minimax results from CSV files written by experiments.run_matches."
    )
    parser.add_argument("--input-dir", default="results", help="directory containing match CSV files")
    parser.add_argument("--output-dir", default="figures", help="directory for generated PNG figures")
    args = parser.parse_args()

    try:
        rows = read_match_rows(args.input_dir)
        aggregates = aggregate_match_rows(rows)
        output_paths = make_plots(aggregates, args.output_dir)
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))

    for output_path in output_paths:
        print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
