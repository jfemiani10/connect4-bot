# Connect Four Bot

Final project for an Intro to AI class, by Jonah Femiani and Ryan.

We build a Connect Four bot using **minimax with alpha-beta pruning** and compare it against simple baseline bots.

## Bots

- **Random:** plays any legal column.
- **Greedy:** wins immediately if it can, blocks the opponent's immediate win if it must, and otherwise plays randomly.
- **Minimax:** looks ahead a set number of moves (the depth) and scores positions with a heuristic. Alpha-beta pruning can be switched on or off.

## Experiments

- Minimax at depths 1–6 against random and against greedy: win rate vs. depth.
- Greedy vs. random: a sanity check on the baselines.
- Minimax with and without alpha-beta: positions searched and time per move vs. depth. Both versions pick the same moves; pruning only makes the search cheaper.

Metrics: win, loss, and draw rate; positions searched per move; seconds per move.

Run a match series from the repository root and save per-game metrics to CSV:

```bash
python3 -m experiments.run_matches --bot1 minimax --bot2 greedy --games 100 --depth 4 --seed 42
python3 -m experiments.run_matches --bot1 minimax --bot2 random --games 100 --depth 6 --no-pruning --output results/minimax_no_pruning.csv
```

The bots alternate who goes first. CSV files include each bot's outcome, move count, total positions searched, and average decision time per move, along with seed and minimax settings.

Generate plots from the match CSV files in `results/`:

```bash
python3 -m experiments.plots
```

The script writes win rate vs. depth, positions searched per move vs. depth, and seconds per move vs. depth to `figures/`. To produce depth curves, run matches at multiple minimax depths; run with and without `--no-pruning` to compare search and timing metrics.

## Usage

Requires Python 3. Install plotting dependencies with `python3 -m pip install -r requirements.txt`.

Run everything from the repo root:

```bash
python3 play.py                          # play the random bot (you go first)
python3 play.py --bot greedy             # play the greedy bot
python3 play.py --bot minimax            # play minimax, looking 4 moves ahead
python3 play.py --bot minimax --depth 6  # stronger, slower minimax
python3 play.py --second                 # the bot goes first
python3 play.py --seed 42                # make the random bot repeatable
python3 -m unittest          # run the tests
```

The board prints as dots for empty cells and colored `O`s for pieces (red for player 1, yellow for player 2). Column numbers run along the bottom, and a `^` marks the last move. Type a column number to play, or `q` to quit.

## Layout

- `play.py`: human vs. bot game in the terminal.
- `src/board.py`: board state and rules (`Board` class).
- `src/display.py`: terminal board display.
- `src/baselines.py`: baseline bots (`RandomBot` and `GreedyBot`).
- `src/minimax.py`: the minimax bot with alpha-beta pruning (`MinimaxBot`).
- `tests/`: unit tests for the board and bots.
- `experiments/`: match and plotting scripts, which write to `results/` and `figures/`.
- `docs/paper_draft.pdf`: mock draft of the final paper, with a checklist of what is left. Rebuild from `paper_draft.tex` with `pdflatex paper_draft.tex` in `docs/`.
- `TODO.md`: the task split between teammates.

**Board convention:** `grid` is 6 rows × 7 columns, with row 0 at the top. Cells hold `0` = empty, `1` = player 1, `2` = player 2.

**Bot interface:** every bot has a `name` and a `choose_move(board)` method that returns a column. Bots must not change the board they're given; to try moves out, use `board.copy()`.
