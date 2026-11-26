# Reversible environment freedom panel results

See PLAN.md for hypotheses registered before each phase. All 296 training runs
terminated normally, and all arms use the same fixed hard target and seed panel.
Total panel wall clock: 70.28 s, on local Mac CPU. Equal compute means equal
policy forward/action slots (307,200 per run), not equal actual actions: first-hit
termination can mask slots. Horizon arms use smaller batches to match slots.
Exact final root probabilities are averaged over eight seeds, computed over the
full finite graph, without outcome-selected checkpoints.

| Reset | Horizon | Switch fraction | Mean root (%) | Median (%) | Max (%) | ≥10% seeds | Mean true actions | Mean episodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| root | 8 | None | 0.0007 | 0.0001 | 0.004 | 0/8 | 307200 | 38400 |
| root_walk4 | 8 | None | 0.0024 | 0.0006 | 0.010 | 0/8 | 307197 | 38400 |
| root_walk4 | 8 | 0.3 | 0.0008 | 0.0003 | 0.004 | 0/8 | 307199 | 38400 |
| root_walk12 | 8 | None | 0.0006 | 0.0006 | 0.001 | 0/8 | 307196 | 38400 |
| root_walk12 | 8 | 0.3 | 0.0007 | 0.0002 | 0.004 | 0/8 | 307199 | 38400 |
| uniform | 8 | None | 0.0115 | 0.0019 | 0.073 | 0/8 | 307105 | 38400 |
| uniform | 8 | 0.3 | 0.0002 | 0.0002 | 0.000 | 0/8 | 307193 | 38400 |
| goal_walk4 | 8 | None | 0.6121 | 0.5006 | 1.100 | 0/8 | 164446 | 38400 |
| goal_walk4 | 8 | 0.3 | 0.5219 | 0.0513 | 3.421 | 0/8 | 288134 | 38400 |
| goal_walk8 | 8 | None | 1.4437 | 1.3309 | 2.277 | 0/8 | 211410 | 38400 |
| goal_walk8 | 8 | 0.3 | 13.1383 | 0.0903 | 97.420 | 1/8 | 297689 | 38400 |
| equal_distance | 8 | None | 0.0001 | 0.0001 | 0.000 | 0/8 | 307200 | 38400 |
| equal_distance | 8 | 0.3 | 0.0007 | 0.0001 | 0.004 | 0/8 | 307200 | 38400 |
| balanced_shell | 8 | None | 1.5901 | 1.7537 | 2.257 | 0/8 | 252167 | 38400 |
| balanced_shell | 8 | 0.3 | 12.5748 | 0.1735 | 61.088 | 2/8 | 302036 | 38400 |
| both_walks | 8 | None | 9.2342 | 1.9727 | 55.305 | 1/8 | 242188 | 38400 |
| both_walks | 8 | 0.3 | 25.2716 | 0.0257 | 97.730 | 3/8 | 299604 | 38400 |
| uniform_goal05 | 8 | None | 3.0119 | 3.3931 | 6.337 | 0/8 | 300596 | 38400 |
| uniform_goal05 | 8 | 0.3 | 13.8393 | 0.0022 | 70.769 | 2/8 | 306966 | 38400 |
| uniform_goal20 | 8 | None | 4.0207 | 3.7120 | 8.554 | 0/8 | 279121 | 38400 |
| uniform_goal20 | 8 | 0.3 | 0.0466 | 0.0065 | 0.325 | 0/8 | 305139 | 38400 |
| goal_walk4 | 8 | 0.1 | 0.0042 | 0.0038 | 0.007 | 0/8 | 305341 | 38400 |
| goal_walk4 | 8 | 0.6 | 67.0848 | 87.9191 | 96.389 | 6/8 | 239594 | 38400 |
| goal_walk4 | 8 | 0.9 | 4.5115 | 3.4304 | 10.243 | 1/8 | 183698 | 38400 |
| balanced_shell | 8 | 0.1 | 0.0009 | 0.0009 | 0.002 | 0/8 | 306666 | 38400 |
| balanced_shell | 8 | 0.6 | 63.7097 | 91.7441 | 97.325 | 7/8 | 284809 | 38400 |
| balanced_shell | 8 | 0.9 | 35.0567 | 31.1115 | 67.746 | 7/8 | 260957 | 38400 |
| root | 16 | None | 5.2576 | 0.0002 | 42.058 | 1/8 | 306156 | 19200 |
| root | 16 | 0.3 | 0.0007 | 0.0001 | 0.004 | 0/8 | 307197 | 32640 |
| root | 32 | None | 5.0709 | 0.0008 | 39.916 | 1/8 | 303340 | 9600 |
| root | 32 | 0.3 | 0.0002 | 0.0002 | 0.000 | 0/8 | 307195 | 29760 |
| root | 64 | None | 0.0013 | 0.0008 | 0.003 | 0/8 | 306821 | 4800 |
| root | 64 | 0.3 | 0.0002 | 0.0002 | 0.000 | 0/8 | 307176 | 28320 |
| root_walk4 | 32 | None | 0.0455 | 0.0006 | 0.329 | 0/8 | 306618 | 9600 |
| root_walk4 | 32 | 0.3 | 0.0002 | 0.0002 | 0.000 | 0/8 | 307181 | 29760 |
| uniform | 32 | None | 0.0129 | 0.0010 | 0.091 | 0/8 | 306695 | 9600 |
| uniform | 32 | 0.3 | 0.0002 | 0.0002 | 0.001 | 0/8 | 307158 | 29760 |

## Distance ladder diagnosis

Fixed goal-walk samples contain only states at distances 1..4. Yet the
continued policy learns to solve unseen-as-reset farther states without any changing
curriculum or reward. At the checkpoints below exact hitting probabilities
are averaged over each shortest-distance shell, then over seeds.

| Mode | Update | Root (%) | d1 | d2 | d3 | d4 | d5 | d6 | d7 | d8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| goal_walk4 / None | 0 | 0.0001 | 9.76 | 1.46 | 0.27 | 0.06 | 0.01 | 0.00 | 0.00 | 0.00 |
| goal_walk4 / None | 75 | 0.0150 | 86.24 | 55.37 | 24.77 | 8.04 | 2.03 | 0.43 | 0.08 | 0.01 |
| goal_walk4 / None | 150 | 0.0718 | 99.28 | 91.58 | 68.30 | 37.57 | 14.74 | 4.32 | 1.04 | 0.15 |
| goal_walk4 / None | 175 | 0.1131 | 99.65 | 94.68 | 75.24 | 45.23 | 19.61 | 6.29 | 1.62 | 0.24 |
| goal_walk4 / None | 200 | 0.1687 | 99.78 | 96.33 | 79.80 | 50.96 | 23.75 | 8.17 | 2.23 | 0.34 |
| goal_walk4 / None | 250 | 0.3443 | 99.90 | 98.00 | 85.61 | 59.33 | 30.49 | 11.52 | 3.41 | 0.54 |
| goal_walk4 / None | 300 | 0.6121 | 99.95 | 98.78 | 89.00 | 65.10 | 35.82 | 14.54 | 4.59 | 0.76 |
| goal_walk4 / 0.6 | 0 | 0.0001 | 9.76 | 1.46 | 0.27 | 0.06 | 0.01 | 0.00 | 0.00 | 0.00 |
| goal_walk4 / 0.6 | 75 | 0.0150 | 86.24 | 55.37 | 24.77 | 8.04 | 2.03 | 0.43 | 0.08 | 0.01 |
| goal_walk4 / 0.6 | 150 | 0.0718 | 99.28 | 91.58 | 68.30 | 37.57 | 14.74 | 4.32 | 1.04 | 0.15 |
| goal_walk4 / 0.6 | 175 | 0.1131 | 99.65 | 94.68 | 75.24 | 45.23 | 19.61 | 6.29 | 1.62 | 0.24 |
| goal_walk4 / 0.6 | 200 | 0.1869 | 99.74 | 95.68 | 77.95 | 48.54 | 21.93 | 7.32 | 1.95 | 0.29 |
| goal_walk4 / 0.6 | 250 | 12.6960 | 99.72 | 95.83 | 78.52 | 49.57 | 23.02 | 7.98 | 2.22 | 0.37 |
| goal_walk4 / 0.6 | 300 | 67.0848 | 98.69 | 92.00 | 72.25 | 44.71 | 21.23 | 7.83 | 2.34 | 0.57 |
| balanced_shell / None | 0 | 0.0001 | 9.76 | 1.46 | 0.27 | 0.06 | 0.01 | 0.00 | 0.00 | 0.00 |
| balanced_shell / None | 75 | 0.0045 | 71.38 | 34.48 | 12.09 | 3.29 | 0.73 | 0.15 | 0.03 | 0.00 |
| balanced_shell / None | 150 | 0.0721 | 96.50 | 83.46 | 56.49 | 28.62 | 10.74 | 3.12 | 0.75 | 0.11 |
| balanced_shell / None | 175 | 0.1359 | 97.84 | 89.35 | 67.03 | 38.57 | 16.53 | 5.43 | 1.44 | 0.23 |
| balanced_shell / None | 200 | 0.2763 | 99.51 | 94.87 | 77.22 | 49.30 | 23.56 | 8.56 | 2.47 | 0.41 |
| balanced_shell / None | 250 | 0.7747 | 99.88 | 98.25 | 87.77 | 64.50 | 36.48 | 15.72 | 5.30 | 1.01 |
| balanced_shell / None | 300 | 1.5901 | 99.96 | 99.33 | 92.93 | 74.33 | 46.84 | 22.65 | 8.55 | 1.83 |
| balanced_shell / 0.6 | 0 | 0.0001 | 9.76 | 1.46 | 0.27 | 0.06 | 0.01 | 0.00 | 0.00 | 0.00 |
| balanced_shell / 0.6 | 75 | 0.0045 | 71.38 | 34.48 | 12.09 | 3.29 | 0.73 | 0.15 | 0.03 | 0.00 |
| balanced_shell / 0.6 | 150 | 0.0721 | 96.50 | 83.46 | 56.49 | 28.62 | 10.74 | 3.12 | 0.75 | 0.11 |
| balanced_shell / 0.6 | 175 | 0.1359 | 97.84 | 89.35 | 67.03 | 38.57 | 16.53 | 5.43 | 1.44 | 0.23 |
| balanced_shell / 0.6 | 200 | 0.2580 | 98.98 | 92.57 | 72.49 | 44.09 | 20.06 | 6.98 | 1.94 | 0.32 |
| balanced_shell / 0.6 | 250 | 29.1511 | 98.98 | 92.37 | 72.24 | 44.39 | 20.76 | 7.55 | 2.22 | 0.46 |
| balanced_shell / 0.6 | 300 | 63.7097 | 97.38 | 87.29 | 64.83 | 38.64 | 17.90 | 6.60 | 1.99 | 0.53 |

## Interpretation and audit

- Switching is sharply schedule dependent. Goal-walk4 continued reaches 0.61%
  exact root success; switching at 10%, 30%, 60%, 90% produces respectively
  0.0042%, 0.52%, 67.08%, 4.51%. Fixed broad balanced shells continued 1.59%,
  with 60% switch 63.71% and 90% switch 35.06%. These are exploratory
  comparisons across one target; do not claim optimal schedule.
- The distance ladder is real in this toy state graph. By step 300 the
  goal-walk-only policy solves 35.82% at exact distance 5, 14.54% at
  distance 6, 4.59% at 7, and 0.76% at 8, despite training resets only
  at distances 1..4. Training rollouts themselves could visit those farther
  states, so these are unseen-as-reset, not necessarily unseen states.
- After removal, root success increases dramatically while shell-wide
  generalization degrades relative to continued training. Thus there is
  transfer to the original target but not a general capability increase
  across all starts after specialization.
- Equal-distance variation has no observed reward or learning advantage
  here. Root walks and uniform also fail to deliver strong root learning.
  Near-goal reward accessibility is important in this bounded sparse task.
- Fixed mixtures can yield breakthroughs without an adaptive selector.
  50/50 root/goal walk yields 25.27% average after 30% switch, 3/8 ≥10%.
  A 5%-goal uniform mix produces 13.84%, while 20% produces only 0.047%.
  This is not monotonic with initial random-policy reward probability.
- Longer horizon at unchanged root sometimes learns optimal paths despite
  relaxed training: 16 and 32 continued each have one strong seed, but
  30% restoration fails and 64 continued no gain at matched action slots.
  Fewer episodes per update with longer horizons is a confound explicitly
  accounted for; this is a compute-matched horizon experiment, not an
  equal-episodes comparison.
- Every trained policy has the same linear architecture, optimizer, fixed
  goal, exact terminal verification, no process reward, and primitive
  action library. All starts are legal, nonterminal. Root/goal walk and
  uniform variants use no exact distances for reset selection; shell
  arms explicitly use an oracle and cannot establish a scalable sampler.
  Float64 exact hitting evaluation uses finite-horizon absorbing recurrence.
- 48 full training trajectories reproduced final weights and all archived train/eval
  records exactly. Every final policy over 10% root probability
  was independently sampled 512 times and action sequences replayed via
  the native environment; all wins are exact eight-gate solutions.
  This validates simulator behavior rather than adding new trained seeds.
- No LLM results and no novelty claim. The environment is a tiny exact
  graph; future transfer claims require independent tasks.

Artifacts: run.py, results.json, audit.py, audit.json, test_run.py, PLAN.md.
Reproduce: python3 run.py then python3 audit.py from this directory.
