# TODO — Connect Four Bot

Target: about 3–5 hours each. See `README.md` for the project description, board convention, and bot interface.

## Both (do first, ~30 min)
- [x] Create the GitHub repo.
- [ ] Add Ryan as a collaborator.
- [x] `Board` interface: `valid_moves()`, `play(col)`, `winner()`, `game_over()`, `copy()`, `grid`, `current_player` (see `src/board.py`).
- [x] Bot interface: `name` and `choose_move(board)` (see `src/baselines.py`).
- [x] Terminal board display (`src/display.py`).

## Jonah: the board and the AI (~3–4 hrs)
- [x] `src/board.py`: board state, dropping pieces, win/draw detection, and tests in `tests/`.
- [x] `src/baselines.py`: the random bot.
- [x] `play.py`: a human vs. bot game in the terminal that calls `print_board` after every move. Pick the opponent with `--bot random`, `--bot minimax --depth N`, or `--bot mcts --iterations N`.
- [x] `src/minimax.py`: depth-limited minimax with a heuristic (score 2- and 3-in-a-rows, prefer the center column).
- [x] Add alpha-beta pruning as an on/off flag, plus a counter for positions searched.
- [x] `--bot` option in `play.py` to choose the opponent.
- [x] `src/mcts.py`: Monte Carlo Tree Search bot (UCB1 selection, random playouts), with tests.
- [ ] Paper: **AI Model and Implementation**, describing both minimax and MCTS and which AI tools were used and how.

## Ryan: baselines and experiments (~3–4 hrs)
- [ ] `src/baselines.py`: the greedy bot (the random bot is already there; follow the same interface). Then add a `"greedy"` line to `BOTS` in `play.py`.
- [ ] `experiments/run_matches.py`: play N games (e.g. 100) between any two bots, alternating who goes first, with fixed seeds. Save win/loss/draw, positions searched (minimax only), and time per move to `results/*.csv`. Matchups:
  - minimax depth 1–6 vs. random and vs. greedy
  - MCTS at 100, 300, 1000, 3000, 5000 iterations vs. random and vs. greedy
  - minimax (depth 2, 4, 6) vs. MCTS (100, 1000, 5000 iterations) head to head
  - greedy vs. random
- [ ] `experiments/plots.py`: make the figures:
  - win rate vs. depth (minimax against random and against greedy)
  - win rate vs. iterations (MCTS against random and against greedy)
  - positions searched vs. depth (with vs. without alpha-beta)
  - time per move vs. depth
  - a table of minimax vs. MCTS head-to-head win rates
- [ ] Paper: **Experimental Setup** and **Experimental Results**.

## Both: wrap up (~1 hr each)
- [ ] Jonah: Abstract and Introduction. Ryan: Conclusion and limitations.
- [ ] References: minimax/alpha-beta and MCTS sources (see the list in `docs/paper_draft.pdf`) and docs for any libraries used.
- [ ] Read each other's sections, then check that every figure is numbered, captioned, and discussed in the text.
- [ ] Final check: a fresh clone plus `pip install -r requirements.txt` reproduces all figures.
