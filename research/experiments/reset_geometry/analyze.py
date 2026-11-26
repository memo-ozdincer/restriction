"""Exact random-walk start distributions and finite-horizon success."""
import json
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "reversible_learning"))
from train import make_environment, HORIZON, ACTIONS


def main():
    transitions, _, root, goal, target = make_environment()
    n = len(transitions)

    def point(index):
        p = np.zeros(n)
        p[index] = 1
        return p

    def evolve(p):
        return np.bincount(transitions.ravel(), weights=np.repeat(p/ACTIONS, ACTIONS),
                           minlength=n)

    def walks(center):
        p = point(center)
        mixture = np.zeros(n)
        for _ in range(4):
            p = evolve(p)
            mixture += p/4
        return mixture

    def distances(center):
        depth = np.full(n, -1, dtype=int)
        depth[center] = 0
        frontier = np.array([center])
        for d in range(1, HORIZON+1):
            candidates = np.unique(transitions[frontier].ravel())
            frontier = candidates[depth[candidates] < 0]
            depth[frontier] = d
        assert np.all(depth >= 0)
        return depth

    goal_depth = distances(goal)
    root_depth = distances(root)
    hit = point(goal)
    for _ in range(HORIZON):
        hit = hit[transitions].mean(axis=1)
        hit[goal] = 1

    exact_shell = (goal_depth == goal_depth[root]).astype(float)
    exact_shell /= exact_shell.sum()
    balanced = np.zeros(n)
    for d in range(1, HORIZON+1):
        shell = goal_depth == d
        balanced[shell] = 1/HORIZON/shell.sum()
    settings = {
        "root": point(root),
        "root_walk_1_4": walks(root),
        "uniform": np.full(n,1/n),
        "goal_walk_1_4": walks(goal),
        "equal_goal_distance": exact_shell,
        "balanced_distance_shells": balanced,
    }
    results = {}
    for name, p in settings.items():
        if name != "root":
            p = p.copy()
            p[goal] = 0
            p /= p.sum()
        results[name] = dict(
            support=int(np.count_nonzero(p)),
            mean_goal_distance=float(p @ goal_depth),
            mean_root_distance=float(p @ root_depth),
            exact_random_policy_success=float(p @ hit),
            goal_distance_distribution=np.bincount(goal_depth, weights=p).tolist(),
        )
    horizon_values = {}
    hit_by_time = point(goal)
    for step in range(1, 65):
        hit_by_time = hit_by_time[transitions].mean(axis=1)
        hit_by_time[goal] = 1
        if step in (8, 12, 16, 24, 32, 64):
            horizon_values[step] = float(hit_by_time[root])
    output = dict(target=list(target), horizon=HORIZON, results=results,
                  ordinary_start_random_success_by_horizon=horizon_values)
    Path(__file__).with_name("results.json").write_text(json.dumps(output, indent=2))
    for k,v in results.items():
        print(k, v["support"], round(v["mean_goal_distance"],3),
              round(v["mean_root_distance"],3), f'{v["exact_random_policy_success"]:.8f}')


if __name__ == "__main__":
    main()
