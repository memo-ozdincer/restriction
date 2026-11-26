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

## Results

Opaque truth-table prompt: 0/12 wins, 8/12 structurally valid circuits.
Semantic description control: 2/8 wins, 5/8 structurally valid circuits.
The successful named responses are majority3 (4 gates, certified optimum)
and parity6 (15 gates, matches feasible bound). The named prompts preserve
the same literal encoding, output specifications and gate budgets.
Each condition sampled once per task with gpt-6-luna, low reasoning effort,
Codex CLI 0.172.0, no tool use allowed. Raw answers, exact prompts, panel,
and summary are in results/. Operational JSONL and stderr files remain
in /tmp/aig-luna-{first,named}-20261126. Screen revisions 76b62eb (opaque)
and 2a8fd3d (named). Neither result supports a statistical pass-rate estimate.

Six exact minima: xor2=3, majority3=4, random0=1, random1=1,
random2=0, random3=2. Random targets collapsed to trivial functions;
the random generator needs better semantic difficulty calibration. Larger
parity/addition cases retain feasible upper bounds and enumeration lower
bounds. No claim of optimum for these six. Next discriminating test:
a symbolic wire-name AIG interface with the same exact semantics to
distinguish literal-number bookkeeping from computational construction.

## Established benchmark setup

Local external sources live beside the repository in ../circuit-tools.
Recreate the pinned setup with ./research/experiments/aig_initial/setup_tools.sh.
ABC revision cd837e9fada8d483b3729569b1b61faa24c5ee5d; EPFL benchmark revision
82d8cc6910419298e713a46644ed59fd3df53038. EPFL MIT license retained.
The extracted panels epfl4.json and epfl8.json each contain 80 distinct
single-output functions (8 per arithmetic circuit), with full input support,
seed 42, original root and cut leaves, source hashes and feasible witnesses.
Each target was independently checked on every assignment against the
source AIG cut using scalar recursive evaluation. This is a reproducible
EPFL-derived panel, not the exact ShortCircuit evaluation split. Original
EPFL designs are not necessarily optimized; cut gate counts are upper bounds.
Use screen.py --panel epfl4.json (with the appropriate path) for frozen
evaluation, optionally --calibration with certified minima. Witnesses stay
outside model prompts.

ShortCircuit (https://arxiv.org/abs/2408.09858) is the directly relevant
published baseline, reporting an AlphaZero-style approach on 500 eight-input
truth tables from EPFL circuits. The exact test split was not obtained.
