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
