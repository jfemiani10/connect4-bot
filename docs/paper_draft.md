# Paper Draft — Connect Four Bot

This is a mock draft of the final paper. It follows the section order of `project-template-letter.docx`, the course's IEEE template. Write and revise the text here, then copy it into the Word template for submission.

- `TODO:` marks something still to be done.
- `[X]` marks a number that has to come from our experiment results. **Never submit a made-up number.**
- The full checklist is at the end of this file.

---

## Title

**Depth versus Strength: Evaluating Minimax with Alpha-Beta Pruning in Connect Four**

TODO: confirm the title. The template says no symbols or special characters in the title.

## Authors

| | Author 1 | Author 2 |
|---|---|---|
| Name | Jonah Femiani | Ryan TODO (surname) |
| Department | TODO | TODO |
| Organization | TODO (university) | TODO (university) |
| City, Country | TODO | TODO |
| Email | TODO (school email) | TODO (school email) |

## Abstract

*The template says no symbols, footnotes, or math in the abstract. Rewrite it once the results are in.*

Board games give a clear, measurable setting for testing how well a search-based agent can plan ahead. We built an agent for Connect Four that uses depth-limited minimax search with a heuristic evaluation function and optional alpha-beta pruning. We compared it against two baseline agents, one that plays randomly and one that greedily takes immediate wins and blocks immediate losses, at search depths from one to six moves. Across [X] games per matchup, the minimax agent won [X] percent of games against the random agent and [X] percent against the greedy agent at depth [X]. Alpha-beta pruning reduced the number of positions searched by [X] percent at depth six without changing the moves chosen. These results show how [TODO: main takeaway, e.g. "a shallow search is already enough to beat simple opponents, while pruning is what makes deeper searches practical"].

**Keywords:** game playing, adversarial search, minimax, alpha-beta pruning, Connect Four

## I. Introduction

Connect Four is a two-player game played on a board seven columns wide and six rows tall. Players take turns dropping pieces into a column, and the first to line up four pieces horizontally, vertically, or diagonally wins. The game is small enough to program in an afternoon but has far too many positions to solve by brute force during play, which makes it a standard setting for studying adversarial search [1]. With perfect play, the first player can always force a win [2], but finding those moves in real time takes search.

Our goal was to measure how much a classic AI method, minimax search, improves play over simple strategies, and what that improvement costs in computation. Specifically, we asked:

1. How does the win rate of a minimax agent change as its search depth increases, against a random opponent and against a greedy opponent?
2. How much does alpha-beta pruning [3] reduce the number of positions searched and the time per move?

We implemented the game, two baseline agents, and a minimax agent in Python, then ran [X] games per matchup with fixed random seeds. TODO: one or two sentences summarizing the main findings once results are in.

## II. Methodology

### A. Data and Preprocessing

This project does not use an external dataset. Instead, the data are the games played between agents. Each matchup between two agents consists of [X] games. The agents alternate who moves first, because the first player has an advantage in Connect Four [2]. Every game uses a fixed random seed, so any game can be replayed exactly by rerunning our scripts.

For each move we record the agent, the search depth, the number of positions searched, and the time taken. For each game we record the winner, or a draw. There is no training step, so no train and test split is needed and there is no risk of data leakage. The minimax agent's evaluation function was designed by hand and was not tuned on the games we report.

TODO: confirm the number of games and the seeds once `experiments/run_matches.py` exists.

### B. AI Model and Implementation

**Game representation.** The board is stored as a six-by-seven grid in which each cell is empty or holds one player's piece. After every move, the program checks only the lines passing through the newly placed piece, since a new win must include that piece.

**Baseline agents.**
- *Random agent:* chooses uniformly among the legal columns.
- *Greedy agent:* plays a winning move if one exists, otherwise blocks the opponent's immediate win if one exists, and otherwise plays randomly.

**Minimax agent.** Minimax [1] explores the tree of possible future moves to a fixed depth. It assumes the agent picks the move with the highest score and the opponent picks the move with the lowest. Won and lost positions get very large positive or negative scores. Positions at the depth limit are scored by a heuristic evaluation function that TODO (Jonah: describe the final heuristic; the plan is to count the agent's open two- and three-in-a-rows minus the opponent's, plus a bonus for pieces in the center column).

**Alpha-beta pruning.** Alpha-beta pruning [3] skips branches of the search tree that cannot affect the final decision. It always returns the same move as plain minimax but usually searches far fewer positions. Our implementation can switch pruning on or off, so the two versions can be compared directly. TODO: mention move ordering (e.g. trying center columns first) if we use it.

**Tools.** The project is written in Python 3 [4]. The game and agents use only the standard library, and figures are made with Matplotlib [5]. Code is at https://github.com/jfemiani10/connect4-bot.

**Use of generative AI.** TODO (required by the course, check its exact wording rules): state which tools were used and how. Draft: *We used Claude Code (Anthropic) to help write the game board, terminal display, random agent, unit tests, and an early draft of this paper's structure. We reviewed, tested, and edited all generated code and text.* Update this to match what was actually used by the end of the project.

## III. Experimental Setup

We ran the following experiments:

1. **Win rate versus depth.** The minimax agent with alpha-beta pruning, at depths 1 through 6, played [X] games against the random agent and [X] games against the greedy agent.
2. **Baseline check.** The greedy agent played [X] games against the random agent, to confirm that the greedy agent is the stronger baseline.
3. **Cost of search.** At each depth, we compared minimax with and without alpha-beta pruning on the same positions, recording positions searched and time per move.

**Metrics.**
- *Win rate:* the fraction of games won (draws reported separately). It measures playing strength.
- *Positions searched per move:* the number of board positions the agent evaluates before choosing a move. It measures computational effort and does not depend on hardware.
- *Time per move:* average seconds per move. It measures practical cost, but depends on hardware.

**Hardware.** TODO: CPU model, RAM, operating system, and Python version of the machine used for the timing results.

## IV. Experimental Results

TODO: fill in after running `experiments/run_matches.py` and `experiments/plots.py`. Every table and figure must be referred to in the text.

**Table I. Win, draw, and loss rates of the minimax agent by search depth.**

| Depth | vs. Random: win / draw / loss (%) | vs. Greedy: win / draw / loss (%) |
|---|---|---|
| 1 | [X] / [X] / [X] | [X] / [X] / [X] |
| 2 | [X] / [X] / [X] | [X] / [X] / [X] |
| 3 | [X] / [X] / [X] | [X] / [X] / [X] |
| 4 | [X] / [X] / [X] | [X] / [X] / [X] |
| 5 | [X] / [X] / [X] | [X] / [X] / [X] |
| 6 | [X] / [X] / [X] | [X] / [X] / [X] |

**Fig. 1. Win rate (%) of the minimax agent versus search depth, against the random and greedy agents.** TODO: insert `figures/win_rate_vs_depth.png`.

**Fig. 2. Average positions searched per move versus search depth, with and without alpha-beta pruning (log scale).** TODO: insert `figures/positions_vs_depth.png`.

**Fig. 3. Average time per move (seconds) versus search depth, with and without alpha-beta pruning.** TODO: insert `figures/time_vs_depth.png`.

TODO: write two or three paragraphs discussing the results. For example:
- At what depth does minimax start reliably beating each baseline (Table I, Fig. 1)?
- How quickly do positions searched grow with depth, and how much does pruning cut that growth (Fig. 2)?
- Does time per move follow the same pattern as positions searched (Fig. 3)?
- Anything unexpected, such as draws or losses at low depth, and why they might happen.
- Greedy versus random result: [X] % win rate for greedy.

## V. Conclusion

TODO: rewrite once the results are in. Do not add any claims that are not supported earlier in the paper.

We built a Connect Four agent based on minimax search with alpha-beta pruning and compared it with random and greedy baselines. [Main result about win rate versus depth.] [Main result about the savings from pruning.]

**Limitations.** We only compared against weak, hand-written opponents, not strong or human players. The evaluation function was designed by hand and was not tuned. Timing results depend on our hardware and on Python's speed.

**Next steps.** Possible extensions include testing against a perfect-play solver, adding move ordering or a transposition table to search deeper, and comparing against a different method such as Monte Carlo Tree Search.

## References

TODO: only keep sources we actually read or used, and check every detail (authors, title, year, DOI or URL). Cite them in the text in the order they first appear.

[1] S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Hoboken, NJ: Pearson, 2020.

[2] L. V. Allis, "A knowledge-based approach of Connect-Four: The game is solved: White wins," M.S. thesis, Vrije Universiteit, Amsterdam, The Netherlands, 1988.

[3] D. E. Knuth and R. W. Moore, "An analysis of alpha-beta pruning," *Artificial Intelligence*, vol. 6, no. 4, pp. 293–326, 1975, doi: 10.1016/0004-3702(75)90019-3.

[4] Python Software Foundation, "Python 3 documentation." [Online]. Available: https://docs.python.org/3/

[5] J. D. Hunter, "Matplotlib: A 2D graphics environment," *Computing in Science & Engineering*, vol. 9, no. 3, pp. 90–95, 2007, doi: 10.1109/MCSE.2007.55.

---

## Checklist: what's left before submission

**Code and experiments** (see `TODO.md` for who does what)
- [ ] Greedy bot (Ryan).
- [ ] Minimax bot with heuristic, alpha-beta on/off flag, and a positions-searched counter (Jonah).
- [ ] `experiments/run_matches.py` writing to `results/*.csv` (Ryan).
- [ ] `experiments/plots.py` producing Figs. 1–3 in `figures/` (Ryan).
- [ ] Run all experiments and record the hardware used.

**Paper content**
- [ ] Fill every `[X]` from the results files.
- [ ] Describe the final heuristic and any move ordering (Section II-B, Jonah).
- [ ] Write the results discussion (Section IV, Ryan).
- [ ] Rewrite the Abstract and Introduction summary with real findings (Jonah).
- [ ] Rewrite the Conclusion with real findings (Ryan).
- [ ] Finalize the generative AI statement, following the course rules.
- [ ] Fill in the author details (department, university, city, email).

**Formatting and checks**
- [ ] Copy everything into `project-template-letter.docx` using the template's styles. Remove the unused author blocks and the template's sample references.
- [ ] No symbols, special characters, footnotes, or math in the title or abstract.
- [ ] Every table and figure is numbered, captioned, and discussed in the text, with units labeled.
- [ ] Every reference is cited in the text, and every citation is in the reference list. Check the reference details.
- [ ] Abbreviations are defined on first use.
- [ ] Each teammate proofreads the other's sections.
- [ ] A fresh clone plus `pip install -r requirements.txt` reproduces every figure.
