# TODO — Connect Four Bot

Target: about 3–5 hours each. See `CLAUDE.md` for the project description and the board convention.

## Both (do first, ~30 min)
- [ ] Create the GitHub repo and add each other as collaborators.
- [ ] Agree on the `Board` interface: `valid_moves()`, `play(col)`, `winner()`, `copy()`, and a `grid` attribute that follows the convention in `CLAUDE.md`.
- [x] Terminal board display (`src/display.py`).

## Jonah: the board and the AI (~3–4 hrs)
- [ ] `src/board.py`: board state, dropping pieces, win/draw detection, and a few tests.
- [ ] `play.py`: a human vs. bot game in the terminal that calls `print_board` after every move. Useful for demos and for checking the bot.
- [ ] `src/minimax.py`: depth-limited minimax with a heuristic (score 2- and 3-in-a-rows, prefer the center column).
- [ ] Add alpha-beta pruning as an on/off flag, plus a counter for positions searched.
- [ ] Paper: **AI Model and Implementation**, including which AI tools were used and how.

## Ryan: baselines and experiments (~3–4 hrs)
- [ ] `src/baselines.py`: the random bot and the greedy bot.
- [ ] `experiments/run_matches.py`: play N games (e.g. 100) between any two bots, alternating who goes first, with fixed seeds. Save win/loss/draw, positions searched, and time per move to `results/*.csv`.
- [ ] `experiments/plots.py`: make the figures:
  - win rate vs. depth (minimax against random and against greedy)
  - positions searched vs. depth (with vs. without alpha-beta)
  - time per move vs. depth
- [ ] Paper: **Experimental Setup** and **Experimental Results**.

## Both: wrap up (~1 hr each)
- [ ] Jonah: Abstract and Introduction. Ryan: Conclusion and limitations.
- [ ] References: a minimax/alpha-beta source (e.g. Russell & Norvig, *AI: A Modern Approach*) and docs for any libraries used.
- [ ] Read each other's sections, then check that every figure is numbered, captioned, and discussed in the text.
- [ ] Final check: a fresh clone plus `pip install -r requirements.txt` reproduces all figures.
