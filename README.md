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

## Usage

Requires Python 3.

Run everything from the repo root:

```bash
python3 play.py              # play against the random bot (you go first)
python3 play.py --second     # the bot goes first
python3 play.py --seed 42    # make the bot's moves repeatable
python3 -m unittest          # run the tests
```

The board prints as dots for empty cells and colored `O`s for pieces (red for player 1, yellow for player 2). Column numbers run along the bottom, and a `^` marks the last move. Type a column number to play, or `q` to quit.

## Layout

- `play.py`: human vs. bot game in the terminal.
- `src/board.py`: board state and rules (`Board` class).
- `src/display.py`: terminal board display.
- `src/baselines.py`: baseline bots. `RandomBot` is done; `GreedyBot` is to do.
- `src/minimax.py`: the minimax bot (to do).
- `tests/`: unit tests for the board.
- `experiments/`: match and plotting scripts, which write to `results/` and `figures/` (to do).
- `TODO.md`: the task split between teammates.

**Board convention:** `grid` is 6 rows × 7 columns, with row 0 at the top. Cells hold `0` = empty, `1` = player 1, `2` = player 2.

**Bot interface:** every bot has a `name` and a `choose_move(board)` method that returns a column. Bots must not change the board they're given; to try moves out, use `board.copy()`.
