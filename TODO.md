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
- [x] `play.py`: a human vs. bot game in the terminal that calls `print_board` after every move. Pick the opponent with `--bot random` or `--bot minimax --depth N`.
- [x] `src/minimax.py`: depth-limited minimax with a heuristic (score 2- and 3-in-a-rows, prefer the center column).
- [x] Add alpha-beta pruning as an on/off flag, plus a counter for positions searched.
- [x] `--bot` option in `play.py` to choose the opponent.
- [ ] Paper: **AI Model and Implementation**, including which AI tools were used and how.

## Ryan: baselines and experiments (~3–4 hrs)
- [x] `src/baselines.py`: the greedy bot (the random bot is already there; follow the same interface). Then add a `"greedy"` line to `BOTS` in `play.py`.
- [x] `experiments/run_matches.py`: play N games (e.g. 100) between any two bots, alternating who goes first, with fixed seeds. Save win/loss/draw, positions searched, and time per move to `results/*.csv`.
- [x] `experiments/plots.py`: make the figures:
  - win rate vs. depth (minimax against random and against greedy)
  - positions searched vs. depth (with vs. without alpha-beta)
  - time per move vs. depth
- [ ] Paper: **Experimental Setup** and **Experimental Results**.

## Both: wrap up (~1 hr each)
- [ ] Jonah: Abstract and Introduction. Ryan: Conclusion and limitations.
- [ ] References: a minimax/alpha-beta source (e.g. Russell & Norvig, *AI: A Modern Approach*) and docs for any libraries used.
- [ ] Read each other's sections, then check that every figure is numbered, captioned, and discussed in the text.
- [ ] Final check: a fresh clone plus `pip install -r requirements.txt` reproduces all figures.
