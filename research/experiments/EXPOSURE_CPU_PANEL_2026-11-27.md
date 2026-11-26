# CPU-ready native exposure panel

User requested independent specifications, implementations and critiques across
the newly discussed domains, with Trillium CPU availability in mind. Three
agents implemented independent domain families and cross-reviewed each other.
All experiments register distinct hypotheses before diagnostics. No full
training panel submitted yet. CPU access verified via trillium-cpu login,
account def-zhijing available; at inspection no user jobs queued. Use one
192-core node for independent seeds, not individual whole-node jobs.
Follow cluster/TRILLIUM_CPU_QUICKSTART.md.

| Domain | Freedom | Initial evidence | Status |
|---|---|---|---|
| Sokoban | Uniform legal or solvable configurations, all boxes retained | Root uniform hit 7.667e-7; solvable resets .04228; all legal .001471 | Ready, strongest state-exposure test |
| Reversible rare 3-wire task | Temporary budget 16/32 vs 8, crossed with near-goal starts | Exact random root hit 1.395e-8→3.494e-4 at H32 | Ready, tests previously failed task with different mechanism |
| Flip | Uniform native configurations or goal walks | Exact random root .00093666, uniform .0155123, near .0753105 | Ready, toy control |
| TSP | Uniform 20–40-city subsets of fixed published 50-city instance | Gain-aware proxy root 60/64 informative vs subset 41/64 | Ready, negative signal-control; auxiliary objective differs |
| 2x2 matrix multiplication GF2 | Intermediate rank9 vs cap8; target rank≤7 unchanged | 1356 reachable ordinary symmetry orbits; exact H32 root hit .0063297; random 1/32 vs 0/32 slack | Ready as mechanism pilot; candidate cost differs |
| 2x2x2 tensor toy | Intermediate cap5 vs cap4 | Uniform hit 51.75% vs 23.61% | Do not allocate full training solely for significance |

Specific designs, sources, constraints, geometry and commands:
- [TSP and Flip](exposure_tsp_puzzles/README.md).
- [Sokoban and tensor](exposure_tensor_sokoban/README.md).
- [Reversible horizon experiment](exposure_reversible_review/README.md).

Independent review:
- TSP and tensor agents both reviewed reversible horizon experiment.
  Identical padded action slots, different episode counts; inherited pooled
  REINFORCE is not a same-state GRPO group. Resource relaxation changes
  the assisted acceptance budget but root evaluation is fixed.
- Reversible and tensor agents reviewed TSP/Flip. Subsets are auxiliary
  tasks; warmup/feature compute differs despite equal padded scoring arrays.
  Fixed TSP50 instance is hard for the proxy's greedy warmup, not established
  to be hard for NICO itself. Flip is a commuting linear puzzle toy.
- Reversible and TSP agents reviewed Sokoban/tensor. Solvable-only resets
  contain feasibility information, hence uniform-all legal reset control.
  Every rank transformation must preserve exactly the target tensor.
  Matrix-specific follow-up review confirms invariants and terminal
  arithmetic replay across 256 input pairs; cap9 changes candidate counts,
  and actual arithmetic is not compute-matched. Group estimator is centered
  REINFORCE. Static review found no blocking correctness errors.

Parent reran 12 unit tests, all pass. All five substantial runners had local
smoke runs by implementers; matrix audit independently checks tensor semantics.
Full learning runs remain pending. Avoid claiming reproduction of state of
the art from these intentionally small policy mechanism screens.
