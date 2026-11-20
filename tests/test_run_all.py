"""Tests for the full experiment plan in experiments/run_all.py."""

import unittest

from experiments.run_all import build_plan


class TestRunAll(unittest.TestCase):
    def test_plan_covers_every_matchup_once(self):
        plan = build_plan()
        filenames = [filename for filename, _ in plan]
        # 24 minimax-vs-baseline + 10 MCTS-vs-baseline + 9 head-to-head + 1 greedy-vs-random
        self.assertEqual(len(plan), 44)
        self.assertEqual(len(set(filenames)), len(filenames))

    def test_no_pruning_runs_use_fewer_games(self):
        for filename, kwargs in build_plan(games=100, no_pruning_games=20):
            expected = 20 if kwargs.get("alpha_beta") is False else 100
            self.assertEqual(kwargs["games"], expected, filename)


if __name__ == "__main__":
    unittest.main()
