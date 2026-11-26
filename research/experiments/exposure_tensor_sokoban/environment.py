"""Exact finite environments for two neutral-exposure mechanism pilots."""
from collections import deque
from itertools import combinations, product
from dataclasses import dataclass

import numpy as np


@dataclass
class Environment:
    name: str
    states: list
    features: np.ndarray
    transitions: np.ndarray  # -1 is padding, self-loop is legal
    terminal: np.ndarray
    distances: np.ndarray  # offline diagnostics/reset construction only
    root: int
    horizon: int
    metadata: dict
    ranks: np.ndarray | None = None


# All nonzero rank-one terms over F2^2 x F2^2 x F2^2.
TERMS = tuple(product(range(1, 4), repeat=3))
TERM_IDS = {term: i for i, term in enumerate(TERMS)}
TENSOR_BITS = tuple(
    sum(((a >> i & 1) * (b >> j & 1) * (c >> k & 1)) << (4*i + 2*j + k)
        for i, j, k in product(range(2), repeat=3))
    for a, b, c in TERMS
)


def tensor_value(state):
    result = 0
    for i in state:
        result ^= TENSOR_BITS[i]
    return result


def tensor_toggle(state, remove, add):
    """Canonical set over F2: a duplicated summand cancels."""
    result = set(state) - set(remove)
    for term in add:
        if 0 in term:
            continue
        result.symmetric_difference_update({TERM_IDS[tuple(term)]})
    return tuple(sorted(result))


def tensor_neighbors(state, cap):
    """Native flip/plus transformations; same types at all caps."""
    destinations = set()
    for p, q in product(state, repeat=2):
        if p == q:
            continue
        a, b = TERMS[p], TERMS[q]
        for axis in range(3):
            if a[axis] == b[axis]:
                # Shared-factor flip: in the two other axes do
                # (x,y)+(z,w) -> (x,y+w)+(z+x,w).
                other = [i for i in range(3) if i != axis]
                u, v = other
                c, d = list(a), list(b)
                c[v] ^= b[v]
                d[u] ^= a[u]
                dest = tensor_toggle(state, (p, q), (c, d))
            else:
                # Plus: replace q by two terms using pivot factor from p.
                c, d = list(b), list(b)
                c[axis] ^= a[axis]
                d[axis] = a[axis]
                dest = tensor_toggle(state, (q,), (c, d))
            if len(dest) <= cap and dest != state:
                destinations.add(dest)
    return sorted(destinations)


def minimum_tensor_ranks():
    ranks = {0: 0}
    for rank in range(1, 5):
        for state in combinations(range(len(TERMS)), rank):
            ranks.setdefault(tensor_value(state), rank)
    return ranks


def tensor_graph(root, goal_rank, cap):
    states = [root]
    index = {root: 0}
    adjacency = []
    target = tensor_value(root)
    for state in states:
        # Absorbing success, consistent with rollout stopping.
        neighbors = tensor_neighbors(state, cap) if len(state) > goal_rank else []
        edges = []
        for dest in neighbors:
            assert tensor_value(dest) == target
            if dest not in index:
                index[dest] = len(states)
                states.append(dest)
            edges.append(index[dest])
        adjacency.append(edges)
    goals = [i for i, state in enumerate(states) if len(state) <= goal_rank]
    distance = reverse_distances(adjacency, goals)
    return states, adjacency, distance


def reverse_distances(adjacency, goals):
    reverse = [[] for _ in adjacency]
    for src, edges in enumerate(adjacency):
        for dest in set(edges):
            reverse[dest].append(src)
    dist = np.full(len(adjacency), -1, dtype=np.int32)
    queue = deque(goals)
    for g in goals:
        dist[g] = 0
    while queue:
        dest = queue.popleft()
        for src in reverse[dest]:
            if dist[src] < 0:
                dist[src] = dist[dest] + 1
                queue.append(src)
    return dist


def padded_edges(adjacency):
    size = max(max(map(len, adjacency)), 1)
    table = np.full((len(adjacency), size), -1, dtype=np.int32)
    for i, edges in enumerate(adjacency):
        table[i, :len(edges)] = edges
        if not edges:
            table[i, 0] = i
    return table


def make_tensor():
    ranks = minimum_tensor_ranks()
    coordinates = tuple(TERM_IDS[t] for t in product((1, 2), repeat=3))
    eligible = []
    for root in combinations(coordinates, 4):
        target = tensor_value(root)
        rank = ranks[target]
        if rank not in (2, 3):
            continue
        states4, _, d4 = tensor_graph(root, rank, 4)
        if d4[0] < 2:
            continue
        states5, _, d5 = tensor_graph(root, rank, 5)
        if len(states5) > len(states4):
            eligible.append((int(d4[0]), root, rank, len(states4), len(states5), int(d5[0])))
    if not eligible:
        raise RuntimeError("no eligible tensor under registered rule")
    distance4, root, rank, count4, count5, distance5 = min(eligible, key=lambda e: (-e[0], e[1]))
    states, adjacency, distances = tensor_graph(root, rank, 5)
    features = np.zeros((len(states), len(TERMS) + 1), dtype=np.float32)
    features[:, -1] = 1
    for i, state in enumerate(states):
        features[i, list(state)] = 1
    term_counts = np.array([len(state) for state in states], dtype=np.int32)
    terminal = term_counts <= rank
    trans = padded_edges(adjacency)
    return Environment("tensor", states, features, trans, terminal, distances, 0,
                       max(8, 2*distance4),
                       dict(target=tensor_value(root), initial_terms=list(root), min_rank=rank,
                            eligible_tensors=len(eligible), cap4_states=count4, cap5_states=count5,
                            cap4_distance=distance4, cap5_distance=distance5,
                            action_encoding="destination state"), term_counts)


BOARD = (
    "#######",
    "#.....#",
    "#.G#..#",
    "#..#..#",
    "#..#G.#",
    "#.....#",
    "#######",
)
DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def board_tiles():
    tiles = tuple((r, c) for r, line in enumerate(BOARD)
                  for c, cell in enumerate(line) if cell != "#")
    ids = {tile: i for i, tile in enumerate(tiles)}
    goals = tuple(sorted(ids[(r, c)] for r, line in enumerate(BOARD)
                         for c, cell in enumerate(line) if cell == "G"))
    return tiles, ids, goals


def sokoban_move(state, action, tiles, ids):
    """Standard walk/push. No pulling; blocked attempts are self-loops."""
    box1, box2, player = state
    boxes = {box1, box2}
    dr, dc = DIRECTIONS[action]
    pr, pc = tiles[player]
    target = ids.get((pr + dr, pc + dc))
    if target is None:
        return state
    if target in boxes:
        r, c = tiles[target]
        beyond = ids.get((r + dr, c + dc))
        if beyond is None or beyond in boxes:
            return state
        boxes.remove(target)
        boxes.add(beyond)
    return (*sorted(boxes), target)


def make_sokoban():
    tiles, ids, goals = board_tiles()
    states = [(a, b, p) for a, b in combinations(range(len(tiles)), 2)
              for p in range(len(tiles)) if p not in (a, b)]
    index = {state: i for i, state in enumerate(states)}
    terminal = np.array([state[:2] == goals for state in states])
    adjacency = [[index[sokoban_move(s, a, tiles, ids)] for a in range(4)] for s in states]
    distances = reverse_distances(adjacency, np.flatnonzero(terminal).tolist())
    max_distance = int(distances.max())
    root = int(np.flatnonzero(distances == max_distance)[0])
    # One-hot position of player, unordered box occupancy, constant.
    L = len(tiles)
    features = np.zeros((len(states), 2*L+1), dtype=np.float32)
    features[:, -1] = 1
    for i, (a,b,p) in enumerate(states):
        features[i, [a,b,L+p]] = 1
    return Environment("sokoban", states, features, np.asarray(adjacency,dtype=np.int32),
                       terminal, distances, root, max_distance+4,
                       dict(board=list(BOARD), tiles=tiles, goals=goals,
                            root_state=states[root], root_distance=max_distance,
                            solvable_states=int((distances >= 0).sum()),
                            legal_states=len(states), terminal_states=int(terminal.sum()),
                            action_encoding="atomic action"))


def make_environment(name):
    if name == "tensor":
        return make_tensor()
    if name == "sokoban":
        return make_sokoban()
    raise ValueError(name)
