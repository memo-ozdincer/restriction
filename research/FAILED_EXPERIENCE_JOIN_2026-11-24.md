# Can failed attempts jointly supply successful training experience?

## Result sought

A pool containing no complete successful proof nevertheless contains complementary
model-written fragments. Joining an unchanged prefix from one failure to an
unchanged suffix from another produces a fully verified proof. Neither original
proof, fragment alone, nor comparable deletion within one attempt solves that
root. We want several concrete examples on real archived training theorems,
not another variant of the closed eight-example constructor curriculum.

This is the first feasibility test of learning from a graph of checked experience:
whole-trajectory binary rewards discard every member of an all-failure pool,
whereas verified connections could supply successful paths and subsequent credit.
This stage only tests whether useful connections exist. It does not perform a
Bellman update, learn a model, establish generalization, or show that search is a
new training paradigm. If it supplies a substantial signal, a separate prospective
training comparison must distinguish experience acquisition, replay and graph
credit, then evaluate an unassisted policy on disjoint theorems.

## Why change direction

D-163 closes the small compiler-generated contract curriculum. Its sparse successes
do not justify more epochs, seeds or representation variants. Earlier source-map
training relied on authored repairs and connections. Here every proposed fragment
must be an exact contiguous slice of a failed original model attempt; no authored
lemma, new tactic, renaming, scope repair or proof-body rewriting is allowed.

Dyna (Sutton, 1990) and prioritized sweeping (Moore and Atkeson, 1993) supply the
older-RL distinction between learning from entire episodes and propagating value
through stored transitions. Our initial implementation is deliberately only a
bounded two-source join. It is not a learned dynamics model or an implementation
of prioritized sweeping. Lean checks the proposed connections and complete proof;
printed goals are not treated as semantic state identities.

## Frozen source and selection

Use the registered C0 training archive: 9,655 train theorem identities, the first
32 proposals each, and its four hash-authenticated logs. Exclude the documented
32 padding proposals. Authenticate statements against the pinned training parquet.
No validation/test outputs or new model samples enter selection.

Eligible roots have all 32 archived correctness flags false, all 32 bodies pass
the conservative single-theorem lexical gate, at least four distinct bodies with
eligible cuts, and a plain named theorem ending in `:= by`. Reuse the existing
conservative prefix-boundary parser: cuts after the first or second top-level
step, retaining at least two following steps and exact bytes. Sort roots by
SHA-256 of `failed-experience-join-20261124/` plus theorem name and take 32.
Freeze all selected raw records, source lines/hashes, cuts and candidate identities
before any new Lean outcomes. Do not replace failed, difficult or timed-out roots.
The original hardcoded Mathlib/Aesop verifier header is preserved; the dataset's
MiniF2F context field was not used by the historical verifier.

For each root, construct at most 128 distinct cross-source bodies, ranked by
SHA-256 of theorem name and body. Prefix and suffix donors must be different
sample indices with different full proof bodies. Exclude bodies identical to an
original attempt. Each body is the exact prefix plus exact suffix, with no new
intervening token. Preserve all donor pairs even when bodies coincide.

Controls are every unique original body, every eligible prefix alone and suffix
alone, and every distinct within-attempt deletion obtained from its eligible cuts
(prefix at an earlier cut plus suffix at a later cut). All controls precede joins;
all generated join candidates run regardless of earlier successes. This is a
bounded acquisition comparison, not matched statistical power or model compute.
Report actual checks and reuse separately; more combinations cost more compute.

## Verification and decision

Use a persistent unchanged Lean REPL with the original import header, resetting
each command to the same imported environment. Record every request and response.
No failed declaration is reused as an environment for another candidate. Never
admit a proof from a pretty-printed goal match, empty goals alone, or an intermediate
proof state. Require command completeness plus the exact theorem's allowed-axiom
report, then independently rerun every accepted original/control/join through the
existing fresh-process verifier. Allowed axioms remain propext, Classical.choice,
Quot.sound. No sorry/admit or verifier changes. Original accepted rechecks are
provenance contradictions and disqualify that root without replacement.

Timeout is 60 seconds per command, with a 300-second cap per root and four CPU
workers. A command timeout terminates that process; remaining checks for the root
are unobserved, not incorrect. No automatic retry or result-dependent budget rise.
The maximum is 32 roots, 1,024 archived proposals and 4,096 join proposals, plus
explicit control checks and independent positive checks. No model sampling or update. The cluster rejects CPU-only Slurm jobs and requires
a GPU reservation. Use one bounded def-zhijing H100 keeper with manual SSH launch
for this CPU workload, then release it; report the idle GPU allocation cost.

The acquisition gate requires at least four fully resolved roots and eight
accepted distinct joined bodies total on those roots, with all originals and
all deletion/prefix/suffix controls rejecting. Each counted join has at least
two distinct source attempts. Review the resulting statements for duplicates or
trivial restatements before any training claim. Report other successes separately,
especially roots solved by deletion alone. If this gate fails, do not launch
training or expand this pool just to turn it positive.

## Sources and interpretation

- Sutton, [Integrated architectures for learning, planning, and reacting](https://mlanthology.org/icml/1990/sutton1990icml-integrated/): planning and actual experience can both support updates. It does not establish that our failed proof fragments connect.
- Moore and Atkeson, [Prioritized sweeping](https://people.eecs.berkeley.edu/~pabbeel/cs287-fa11/optreadings/MooreAtkeson-1993-prioritized-sweeping.pdf): predecessor structure supports value propagation in modeled Markov problems. Exact theorem-state dependence makes a text-only equivalence insufficient here.
- Anthropic, [Training Alignment Auditors via Reinforcement Learning](https://alignment.anthropic.com/2026/training-alignment-auditors/), October 15, 2026: reports transfer to a different scaffold and convergence toward systematic controlled investigations. Our inference is to require unassisted transfer later, not to treat diversity or search success as learning.
- Hou et al., [Rethinking RL Generalizes, SFT Memorizes](https://arxiv.org/abs/2611.14912), November 17 revision: its abstract reports that data source and scale change SFT/RL generalization comparisons. Only the abstract has been inspected here; no theorem or detailed causal conclusion is adopted. This reinforces preserving a same-data replay comparison if acquisition succeeds.

Publish source, frozen data, all failures and successful complete programs. Keep
the broad research goal open regardless of this screen's result.
