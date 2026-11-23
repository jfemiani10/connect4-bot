"""Monte Carlo Tree Search (MCTS) bot.

THE BIG IDEA
------------
To judge a move, it plays lots of quick random games ("playouts" or "simulations") 
starting from that move and counts how often they're won. A move that wins 70% of 
random moves is probably / statistically better than one that wins 30%.
Playing random games from every move equally would waste time on obviously
bad moves, so MCTS builds a search tree as it goes and spends more of its
playouts on the moves that look promising. Each pass ("iteration") has four
steps:

SELECTION: Start at the root (the current position) and walk down
the tree, at each step picking the child with the best
UCB1 score (explained below), until reaching a node that
still has untried moves, or a finished game.

EXPANSION: Add ONE new child node for one of those untried moves.

SIMULATION: From that new node, play random moves until the game
ends (a "playout").

BACKPROPAGATION: Walk back up to the root, updating every node on the
path: one more visit, plus a win if the playout was won
by the player who made that node's move.

After all iterations, the bot plays the move whose node was VISITED the
most. Visits are a more reliable sign of a good move than the raw win rate,
because a move with a high win rate but only a few visits may just be lucky.
"""

import math
import random


class Node:
    """One position in the MCTS search tree.
    Each node is the position reached by playing `move` from its parent.
    It stores the statistics MCTS uses to judge how good that move was.
    """

    def __init__(self, board, parent=None, move=None):
        self.board = board # the position at this node (a Board copy)
        self.parent = parent # the node above, or None at the root
        self.move = move # the column played to get here from the parent
        self.children = [] # nodes for moves already tried from here
        self.untried_moves = board.valid_moves() # moves not yet expanded

        # The player who made `move`. Wins are counted from their point of
        # view, because that's who the parent is deciding for when it
        # compares its children.
        self.player_just_moved = 3 - board.current_player

        self.visits = 0 # how many playouts passed through this node
        self.wins = 0.0 # playouts won by player_just_moved (draws count 0.5)

    def is_fully_expanded(self):
        return not self.untried_moves

    def ucb1(self, c):
        """UCB1 score of this node, used by its parent during selection."""
        exploitation = self.wins / self.visits
        exploration = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration


class MCTSBot:
    """Picks moves with Monte Carlo Tree Search.
    ITERATIONS: how many select/expand/simulate/backpropagate passes to run
    per move. More is stronger but slower.
    C = the exploration constant in UCB1 (see the top of this file).
    SEED = seed for the random moves, so results can be repeated.
    """

    def __init__(self, iterations=1000, c=math.sqrt(2), seed=None):
        self.iterations = iterations
        self.c = c
        self.rng = random.Random(seed)
        self.name = f"MCTS ({iterations} iterations)"

    def choose_move(self, board):
        # The root is the current position. We work on a copy so the real
        # board is never changed.
        root = Node(board.copy())

        for _ in range(self.iterations):
            node = self._select(root)
            node = self._expand(node)
            result = self._simulate(node.board)
            self._backpropagate(node, result)

        # Play the most-visited move (see "THE BIG IDEA" above for why).
        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.move

    def _select(self, node):
        """Step 1: walk down the tree, following the best UCB1 score.
        Stops at the first node that still has untried moves (so it can be
        expanded) or that is a finished game (nothing left to expand).
        """
        while node.is_fully_expanded() and node.children:
            node = max(node.children, key=lambda child: child.ucb1(self.c))
        return node

    def _expand(self, node):
        """Step 2: add one child for a random untried move, and return it.
        If the game is already over at this node, there's nothing to add,
        so the node itself is returned and simulated as-is.
        """
        if node.board.game_over():
            return node

        move = self.rng.choice(node.untried_moves)
        node.untried_moves.remove(move)

        child_board = node.board.copy()
        child_board.play(move)
        child = Node(child_board, parent=node, move=move)
        node.children.append(child)
        return child

    def _simulate(self, board):
        """Step 3: play random moves to the end of the game.
        Returns the winner (1 or 2), or None for a draw. Works on a copy so
        the tree's stored position isn't changed.
        """
        board = board.copy()
        while not board.game_over():
            board.play(self.rng.choice(board.valid_moves()))
        return board.winner()

    def _backpropagate(self, node, winner):
        """Step 4: update visit and win counts from `node` back up to the root.
        Each node counts the result from the point of view of the player who
        made its move: a win for them is 1, a draw is 0.5, a loss is 0.
        """
        while node is not None:
            node.visits += 1
            if winner is None:
                node.wins += 0.5
            elif winner == node.player_just_moved:
                node.wins += 1
            node = node.parent
