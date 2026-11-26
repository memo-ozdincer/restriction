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

ABC was built successfully as native arm64 on this Mac (ABC 1.01). Its
twoexact -a mode confirms XOR2 at 3 AND gates and majority3 at 4, rejecting
the respective 2- and 3-gate bounds. ABC also reads the original EPFL adder
(256 inputs, 129 outputs, 1020 AND nodes). Exact parity4 lower-bound search
with the default SAT backend exceeded its requested three-second limit and
was stopped; no optimality conclusion is recorded for it. Use an external
subprocess timeout when running larger exact synthesis jobs.

## Terra comparison

Hypothesis registered before sampling: Terra's stronger reasoning may reduce
numeric AIG bookkeeping failures and increase correct circuits relative to
Luna under identical prompts and low reasoning effort. Run both original
prompt variants on gpt-6.1-terra (the model used in the prior Terra experiments).
A separate EPFL-derived screen checks whether this ability transfers to
unnamed real-circuit functions. One attempt per target remains exploratory.

Terra result (gpt-6.1-terra, low effort, one attempt per condition/task):
opaque 8/12, named 8/8, EPFL sample 4/8 (4/4 four-input, 0/4
eight-input). All 28 responses were structurally valid, including incorrect
zero-gate submissions. All 20 matched prompts byte-identical to Luna's
prior runs; every archived answer independently reverified. Terra improved
the feasible 3-bit addition bound from 22 to 17 gates, 4-bit addition
31 to 24, and sampled four-input multiplier cut from 4 to 3. These are
new feasible bounds, not proven minima. All six originally certified
tasks solved optimally in opaque format. Four EPFL samples per width
chosen at indices 0,24,48,72 from the fixed panel (adder, hypotenuse,
multiplier, square). The eight-input failures all returned zero gates,
so interpretation/engagement with opaque large truth tables remains a
confound. Raw compact evidence in results/terra-{opaque,named,epfl};
operational logs local /tmp/aig-terra-{opaque,named,epfl}-20261126.
No training. Screen commit 66c8c27.

## Frozen random-start pilot

Registered hypothesis: target-independent pre-existing computational objects
can increase terminal completion success by exposing a model to a different
starting state. Compare Luna root vs Luna scrambled and Terra root vs Terra
scrambled, using the same eight previously sampled EPFL functions and one
rollout per condition. The root budget is witness gate count + 2 in ALL
conditions to guarantee feasibility even if both supplied gates are unused.
Count every supplied gate against the budget. Random starts use seed
20261126, two random legal AND gates, rejection only for duplicate or constant
truth tables (including complements). No target or reference circuit consulted
by sampler. Both models receive the identical starts. The fixed prefix cannot
be edited; outputs and new gates use the unchanged evaluator. The original
root-only witness remains feasible after shifting its internal literal IDs.
This is a frozen inference diagnostic; no trained-policy transfer is measured.
