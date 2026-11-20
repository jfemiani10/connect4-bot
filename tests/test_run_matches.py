"""Tests for the experiment match runner."""

import csv
import os
import tempfile
import unittest

from experiments.run_matches import CSV_FIELDS, run_matches


class TestRunMatches(unittest.TestCase):
    def test_alternates_starts_and_writes_per_game_metrics(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "matches.csv")
            rows, written_path = run_matches(
                "random", "greedy", games=4, seed=12, output_path=output_path
            )

            self.assertEqual(written_path, output_path)
            self.assertEqual([row["bot1_player"] for row in rows], [1, 2, 1, 2])
            self.assertEqual([row["bot2_player"] for row in rows], [2, 1, 2, 1])
            self.assertEqual([row["seed"] for row in rows], [12, 13, 14, 15])

            with open(output_path, newline="", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                self.assertEqual(reader.fieldnames, CSV_FIELDS)
                saved_rows = list(reader)
            self.assertEqual(len(saved_rows), 4)
            for row in saved_rows:
                self.assertEqual(int(row["moves"]), int(row["bot1_moves"]) + int(row["bot2_moves"]))
                self.assertIn(row["bot1_result"], ("win", "loss", "draw"))
                self.assertIn(row["bot2_result"], ("win", "loss", "draw"))
                self.assertIn(row["winner"], ("bot1", "bot2", "draw"))
                self.assertGreaterEqual(float(row["bot1_seconds_per_move"]), 0)
                self.assertGreaterEqual(float(row["bot2_seconds_per_move"]), 0)

    def test_rejects_non_positive_game_count(self):
        with self.assertRaises(ValueError):
            run_matches("random", "greedy", games=0)

    def test_supports_same_bot_on_both_sides(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "same-bot.csv")
            rows, _ = run_matches(
                "random", "random", games=2, seed=5, output_path=output_path
            )

            for row in rows:
                self.assertEqual(row["moves"], row["bot1_moves"] + row["bot2_moves"])
                self.assertGreater(row["bot1_moves"], 0)
                self.assertGreater(row["bot2_moves"], 0)

    def test_records_minimax_searches(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "minimax.csv")
            rows, _ = run_matches(
                "minimax", "random", games=1, depth=1, output_path=output_path
            )

        self.assertGreater(rows[0]["bot1_positions_searched"], 0)
        self.assertEqual(rows[0]["bot2_positions_searched"], 0)
        self.assertEqual(rows[0]["depth"], 1)
        self.assertTrue(rows[0]["alpha_beta"])

    def test_each_bot_plays_its_own_moves_in_both_seats(self):
        # Only minimax searches positions, so in every game, whichever seat
        # bot1 is in, all searching must be credited to bot1 (minimax).
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "seats.csv")
            rows, _ = run_matches(
                "minimax", "random", games=4, depth=1, output_path=output_path
            )

        self.assertEqual([row["bot1_player"] for row in rows], [1, 2, 1, 2])
        for row in rows:
            self.assertGreater(row["bot1_positions_searched"], 0)
            self.assertEqual(row["bot2_positions_searched"], 0)

    def test_runs_mcts_and_records_iterations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "mcts.csv")
            rows, _ = run_matches(
                "mcts", "random", games=4, iterations=200, output_path=output_path
            )

        for row in rows:
            self.assertEqual(row["iterations"], 200)
            # MCTS should beat a random bot from either seat.
            self.assertEqual(row["bot1_result"], "win")

    def test_rejects_non_positive_iterations(self):
        with self.assertRaises(ValueError):
            run_matches("mcts", "random", games=1, iterations=0)


if __name__ == "__main__":
    unittest.main()
