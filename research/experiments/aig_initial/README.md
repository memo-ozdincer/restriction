# Initial AIG difficulty screen

Hypothesis registered before sampling: Luna can construct small familiar
Boolean circuits but its verified success rate falls on larger parity and
multi-output arithmetic circuits even at demonstrated feasible budgets.
This identifies candidates for later state-exposure experiments.

The local evaluator checks every input assignment using integer bitsets.
A literal is twice the node index plus an inversion bit. Node zero is
constant false. Every AND costs one gate, including supplied prefix gates.
No process score. Witnesses establish upper bounds, not optimality claims.
The initial panel contains 12 tasks, including four random generated targets.
The runner sends only public target tables, never witnesses. Each attempt
uses a fresh Codex CLI invocation with isolated cwd and read-only sandbox.

The historical Lean preflight was attempted; its cluster-specific dependencies
are unavailable locally. This Python-only environment does not require them.

Run tests: python3 -m unittest discover -s research/experiments/aig_initial
Run screen: python3 research/experiments/aig_initial/screen.py --out /tmp/aig-screen

Exact calibration: run optimal.py in this directory. Breadth-first enumeration
quotients available truth tables by free inversion and eliminates duplicate
functions, which cannot improve minimum gate count. The 250,000-state cap is
a computational limit, not an optimality certificate. Certified tasks use
their exact minimum in the screen; other tasks use the feasible witness bound.
The frozen screen records correctness and gate counts separately, and ratio
reward for certified minima (zero optimum has reward 1 only for zero gates).
Hypothesis: the exact calibrated tasks expose format competence, while longer
arithmetic tasks test compositional construction. One attempt per task is
an initial diagnostic, not an estimate of a stable pass rate.

Follow-up hypothesis registered after seeing the first six opaque truth-table
attempts: describing the same arithmetic function in words, alongside the
unchanged truth table, may separate numeric truth-table interpretation from
AIG construction difficulty. Run with --named for the eight structured tasks;
this is a prompt-format comparison, not an RL intervention.
