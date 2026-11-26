"""Exact deterministic 8-puzzle dynamics and reset calibration."""
from collections import deque, Counter
from typing import Iterable

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
MOVES = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


def validate(board):
    board = tuple(board)
    if sorted(board) != list(range(9)):
        raise ValueError("board must be a permutation of 0 through 8")
    return board


def move(board, action):
    if not isinstance(action, str) or action not in MOVES:
        raise ValueError("unknown move")
    i = board.index(0)
    r, c = divmod(i, 3)
    dr, dc = MOVES[action]
    r += dr
    c += dc
    if not 0 <= r < 3 or not 0 <= c < 3:
        raise ValueError("blank would leave board")
    j = 3 * r + c
    result = list(board)
    result[i], result[j] = result[j], result[i]
    return tuple(result)


def neighbors(board):
    i = board.index(0)
    r, c = divmod(i, 3)
    for action, (dr, dc) in MOVES.items():
        if 0 <= r + dr < 3 and 0 <= c + dc < 3:
            yield action, move(board, action)


def distances(goal=GOAL):
    goal = validate(goal)
    depth = {goal: 0}
    queue = deque([goal])
    while queue:
        state = queue.popleft()
        for _, nxt in neighbors(state):
            if nxt not in depth:
                depth[nxt] = depth[state] + 1
                queue.append(nxt)
    return depth


def execute(board, actions: Iterable[str]):
    board = validate(board)
    for action in actions:
        board = move(board, action)
    return board


def verify(board, actions, budget, goal=GOAL):
    if not isinstance(actions, (list, tuple)):
        raise ValueError("actions must be an array")
    final = execute(board, actions)
    correct = final == validate(goal)
    return dict(correct=correct, moves=len(actions), within_budget=len(actions) <= budget,
                reward=int(correct and len(actions) <= budget), final=final)


if __name__ == "__main__":
    depth = distances()
    assert len(depth) == 181440 and max(depth.values()) == 31
    print(len(depth), max(depth.values()), sorted(Counter(depth.values()).items()))
