"""Tests for aggregating and plotting match-runner CSV data."""

import csv
import os
import tempfile
import unittest

from experiments.plots import (
    aggregate_head_to_head,
    aggregate_match_rows,
    aggregate_mcts_rows,
    make_mcts_plots,
    make_plots,
    read_match_rows,
)
from experiments.run_matches import CSV_FIELDS, run_matches


def match_row(game, opponent, depth, alpha_beta, result, moves, positions, seconds):
    row = {field: "" for field in CSV_FIELDS}
    row.update({
        "game": game,
        "bot1": "minimax",
        "bot2": opponent,
        "depth": depth,
        "alpha_beta": alpha_beta,
        "bot1_result": result,
        "bot2_result": "loss" if result == "win" else "win",
        "bot1_moves": moves,
        "bot2_moves": moves,
        "bot1_positions_searched": positions,
        "bot2_positions_searched": 0,
        "bot1_seconds_per_move": seconds,
        "bot2_seconds_per_move": 0,
    })
    return row


class TestPlots(unittest.TestCase):
    def test_aggregates_minimax_by_depth_opponent_and_pruning(self):
        rows = [
            match_row(1, "random", 2, True, "win", 10, 100, 0.2),
            match_row(2, "random", 2, True, "loss", 20, 200, 0.1),
            match_row(3, "greedy", 2, False, "draw", 10, 400, 0.4),
        ]

        aggregates = aggregate_match_rows(rows)

        self.assertEqual(aggregates[("random", 2, True)]["win_rate"], 0.5)
        self.assertEqual(aggregates[("random", 2, True)]["mean_positions_per_move"], 10)
        self.assertAlmostEqual(aggregates[("random", 2, True)]["mean_seconds_per_move"], 2 / 15)
        self.assertEqual(aggregates[("greedy", 2, False)]["win_rate"], 0)

    def test_reads_csv_and_writes_all_three_figures(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "results")
            output_dir = os.path.join(temp_dir, "figures")
            os.makedirs(input_dir)
            csv_path = os.path.join(input_dir, "matches.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
                writer.writeheader()
                writer.writerow(match_row(1, "random", 1, True, "win", 10, 50, 0.01))
                writer.writerow(match_row(2, "greedy", 2, False, "loss", 12, 100, 0.02))

            rows = read_match_rows(input_dir)
            paths = make_plots(aggregate_match_rows(rows), output_dir)

            self.assertEqual(len(paths), 3)
            self.assertTrue(all(path.is_file() and path.stat().st_size > 0 for path in paths))


class TestMCTSPlots(unittest.TestCase):
    def test_mcts_and_head_to_head_from_real_matches(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "results")
            output_dir = os.path.join(temp_dir, "figures")
            # MCTS in either seat (bot1 or bot2) must be found.
            run_matches("mcts", "random", games=2, iterations=50,
                        output_path=os.path.join(input_dir, "a.csv"))
            run_matches("greedy", "mcts", games=2, iterations=100,
                        output_path=os.path.join(input_dir, "b.csv"))
            run_matches("minimax", "mcts", games=2, depth=2, iterations=50,
                        output_path=os.path.join(input_dir, "c.csv"))
            rows = read_match_rows(input_dir)

            mcts = aggregate_mcts_rows(rows)
            self.assertEqual(set(mcts), {("random", 50), ("greedy", 100)})
            self.assertEqual(mcts[("random", 50)]["games"], 2)

            paths = make_mcts_plots(mcts, output_dir)
            self.assertEqual(len(paths), 2)
            self.assertTrue(all(path.is_file() and path.stat().st_size > 0 for path in paths))

        summary = aggregate_head_to_head(rows)
        self.assertEqual(len(summary), 1)
        entry = summary[0]
        self.assertEqual((entry["minimax_depth"], entry["mcts_iterations"], entry["games"]), (2, 50, 2))
        self.assertAlmostEqual(
            entry["minimax_win_rate"] + entry["draw_rate"] + entry["mcts_win_rate"], 1.0
        )


if __name__ == "__main__":
    unittest.main()
