# Capability retention and applications

Audit date: 2026-09-12. This is a research assessment and a completed-training
analysis, not registration or submission of a new GPU experiment.

## What has actually run

Final update at 15:53 EDT: evaluation `902538` completed at 15:52:29,
Slurm exit 0, elapsed 08:31:13. Both frozen analyses succeeded and the GPU
allocation ended. The running-job description below is historical.

## Final held-out comparison

All conditions use the same 467 theorems and 128 proposals each (59,776
registered attempts per condition). C2 and C3 both solve 277, with 276 shared
solves. C2 alone solves `numbertheory_aoddbdiv4asqpbsqmod8eq1`; C3 alone solves
`aime_1983_p1`. Each exclusive solve has only one correct observation.

| Measure | C2 soft unlikeliness | C3 zero-advantage blocking |
|---|---:|---:|
| Correct proposals | 27,637 | 27,997 |
| Correct tactic modes | 12,006 | 10,444 |
| Expected modes at 16 correct draws, 259 common eligible theorems | 10.9667 | 10.1568 |
| Solved at 128 | 277 | 277 |

C2 has higher coverage at all six frozen representations. C3 has 0.602
percentage points more correct proposals, but 13.01% fewer raw modes and
7.38% fewer rarefied modes relative to C2. The registered verdict is
`heldout_soft_unlikeliness_outperforms_hard_blocking`. This is a syntactic
exploration verdict, not universal superiority on proof quality.

Symmetric exploratory recovery, restricted to base patterns unobserved in C1:

| Representation / minimum base count | C2 only | C3 only | Both | Neither |
|---|---:|---:|---:|---:|
| Tactic modes / 1 | 847 | 715 | 691 | 5,542 |
| Tactic modes / 4 | 31 | 24 | 93 | 17 |
| Tactic modes / 8 | 4 | 1 | 22 | 1 |
| Exact strings / 1 | 337 | 545 | 106 | 21,680 |
| Exact strings / 4 | 4 | 2 | 9 | 2 |

There is a characteristic distinction worth inspecting: C3 recovers more exact
base strings when singleton base observations count, despite C2's broader
tactic coverage. That direction reverses for repeatedly observed exact strings.
This motivates checking whether C3 stays closer to base wording while C2
generates more variants, not claiming that C3 preserves deeper mathematics.
On miniF2F alone, repeated (>=4) base tactic modes recovered only by C3 number
11 versus 9 only by C2: a small descriptive subgroup, not a selected benchmark
win. These are finite-sample support estimates, not proven forgotten abilities.

Infrastructure-class failures were 468/59,776 for C2 and 507/59,776 for C3;
they remain counted as failed attempts. No selective retries were performed.
C1 has different optimizer settings; C2/C3 are the matched comparison.
C5 reward rejection still has no eligible full result.

Artifacts: `results/c2_unlikeliness_vs_c3_seed42_pass128.json`, SHA-256
`7e7ab1a77cf01a5ef5ba8ff1cd3dc631af8bf818bf81d6d09aa1c2b5e77d9d72`;
`results/symmetric_recovery_c0_c1_c2_c3_seed42_pass128.json`, SHA-256
`d87ecacd5afb0b8af0adfe7eb9341b5d78b3c610e942ece522e2b8af9f3db77a`.
The latter is reproducible with `scripts/project/analyze_symmetric_recovery.py`
using the four finalized runs; it validates hashes, panels, budgets, and metrics.

## Earlier running-job audit

C2 job `902537` completed September 11 at 15:22 EDT after 23:11:43.
All 604 steps finalized, with 308,960 registered proposals on 9,655 theorems.
Its pass@128 evaluation job `902538` was running on `trig0026` at the audit,
about 7 hours 23 minutes into execution, without finalized evaluation metrics.
The immutable job will write the registered training and evaluation comparisons
after evaluation succeeds. We did not change that job or inspect partial
held-out quality to select a new experiment.

Matched no-exploration control `875440` and C5 retry `876746` remain canceled
at zero runtime since September 2. C5 has an engineering smoke result but no
eligible full training result. The new completed comparison is C2 versus C3,
not C2 versus C5.

The existing frozen training analyzer was executed separately, with its output
under the completed C2 run so it cannot collide with the running job's
registered result paths:

`runs/c2-unlikeliness-2-full-20260909-seed42-bc282d6-h100-workers64/comparison-audit-20260912.json`

SHA-256: `fa1c33bc07861e89a54982ecedb66363611d6fcab5ff6642ec88640d9c7a84c4`.
Its completion, proof-log, archive and mechanism gates passed. These are
on-policy training observations; final-policy claims await evaluation.

| Training measure | C1 default GRPO | C2 unlikeliness | C3 zero advantage |
|---|---:|---:|---:|
| Correct proposals | 215,482 | 204,164 | 211,635 |
| Correct tactic modes | 34,336 | 75,180 | 53,825 |
| Exact normalized correct proofs | 66,515 | 148,845 | 111,570 |
| Solved at 32 training proposals | 7,932 | 8,124 | 8,078 |

On 6,594 common theorems with at least 16 correct draws, expected mode coverage
at exactly 16 correct draws is C2 7.4585 versus C3 5.4732. C3 is 26.6% lower.
C2 also wins within the archive-eligible stratum (5.4349 versus 3.7994) and
ineligible stratum (7.7677 versus 5.7289). The preregistered training rule
classifies this as `soft_unlikeliness_outperforms_hard_blocking`.

From steps 1--100 to 501--600, modes per correct rollout rise from 0.358 to
0.385 for C2 and decline from 0.317 to 0.229 for C3. These windows contain
different theorems, so they describe training trajectories rather than repeated
measurements of identical theorem-level support. C1's previously recorded
trajectory falls from approximately 0.325 to 0.104.

A descriptive scan of the first 32 proposals per training theorem found
`nlinarith` among parsed heads in 33.41% / 30.64% / 33.20% of correct C1/C2/C3
proofs. `have` appears in 9.58% / 12.96% / 10.92%. Mean generated token counts
are 41.38 / 37.35 / 39.11. These are marginal syntax summaries, affected by
which theorems yield correct samples and by the parser. They do not show C3
uniquely moving toward abstract or intricate mathematics. C1 also differs in
PPO epochs and KL; C2/C3 share those settings.

C3 does contain complementary support: it recovers 2,742 of 8,477 C0 modes
observed at least twice and absent from C2, and 725 of 1,563 at frequency four.
This alone is not superiority: the reverse direction and downstream utility
must also be measured.

## What would make reward rejection useful?

If efficiency or elegance can be measured reliably, optimizing that objective
directly is the natural baseline. Rarity alone does not imply usefulness.
Blocking is more compelling when we can identify an overused shortcut but
cannot yet score which alternative will transfer to an unknown future task.

C5 implements the user's intended training rejection:

`training_reward = Lean_correct AND NOT archived_blocked_mode`.

Lean still reports mathematical correctness independently. A blocked correct
proof earns zero training reward, like an invalid proof; if an unblocked
correct alternative is in the group, normal group-relative normalization gives
the blocked proof negative advantage. This is reward rejection, not a
decoding constraint or a guarantee that its probability becomes zero. If no
accepted positive is sampled, there is no positive alternative signal.

The distinguishing hypothesis is persistent exclusion by proof class. A rare
wording of the same blocked class still earns zero, whereas likelihood rank
can reward an unlikely wording of a familiar approach. Soft exploration could
also operate on semantic classes or use persistent counts; this is a testable
design choice, not a property impossible for other methods to reproduce.

The implementation currently blocks one frozen, theorem-specific C0 signature
on 1,014 training theorems. It is neither an iterative expanding archive nor a
general detector of mathematical shortcuts. Tactic signatures do not reliably
identify semantic strategy. Moreover, useful capabilities absent from the
training tasks receive no direct rehearsal merely because another proof is
blocked. Consequently C5 might preserve, replace, or further suppress base
skills. General capability retention cannot be assumed from its objective.

## Focused literature evidence

- [Rewarding the Unlikely](https://arxiv.org/html/2506.02355v2) already reports
  improved deep sampling and diversity recovery under soft rank rewards.
  Thus those phenomena alone cannot distinguish our method. The paper also
  shows benefits from multiple PPO epochs, reinforcing the need for the
  matched optimizer control.
- [Does RL Really Incentivize Reasoning Capacity Beyond the Base Model?](https://arxiv.org/abs/2504.13837)
  documents cases where RL improves small-k
  success while reducing coverage at large k. This motivates testing lost
  sampled support; it does not establish our desired cross-domain causal
  mechanism or prove literal erasure of skills.
- [The Entropy Mechanism of RL](https://arxiv.org/abs/2505.22617) motivates
  Clip-Cov and KL-Cov to manage entropy collapse. This is a strong competing
  explanation and a useful later comparator, rather than a reason to presume
  blocking is necessary.
- [Go-Explore](https://www.nature.com/articles/s41586-020-03157-9) establishes
  the value of retaining and returning to promising states in difficult
  exploration. Its explicit archive retains access; our rejection archive
  removes training reward for selected modes. Its success is not evidence
  that rejecting familiar proofs prevents forgetting.
- [DIAYN](https://arxiv.org/abs/1802.06070) learns diverse skills with downstream
  uses. It supports the broader idea of learning a useful repertoire without
  knowing the final task reward, but is not a GRPO cross-domain benchmark.

The closest concrete dataset precedent found is in
[Goedel-Prover, Section 4](https://arxiv.org/html/2502.07640v1). ProofNet
performance correlates weakly with competition benchmarks. Adding Mathlib
training changes ProofNet from 13.3% to 15.6%, while miniF2F drops from 56.6%
to 54.1%. This is supervised expert iteration, not the desired GRPO forgetting
experiment. It nevertheless provides a substantive prior for competition
mathematics versus undergraduate mathematics as a domain-shift test.

## Dataset audit and recommendation

Overlap checks compare names and statement text after removing declaration
names and whitespace. They are preliminary syntactic checks, not semantic
deduplication or a pretraining-contamination audit.

| Local candidate | Rows | Training-name overlap | Normalized statement matches |
|---|---:|---:|---:|
| mff-lwb-goedel-holdout-800 | 800 | 246 | 378 |
| mff-lwb-unseen-200 | 200 | 0 | 0 |
| miniF2F-test | 244 | 0 | 0 |
| Bundled ProofNet | 371 | 0 | 0 |

The 800-row filename does not establish a held-out split for this experiment.
The 200-row slice is a convenient unused training-disjoint diagnostic but
still needs its role and overlap with existing evaluation checked. miniF2F is
already measured and shows a modest effect: at pass@128 base solves 123,
GRPO 121, C3 123. It does not demonstrate a large cross-domain failure.

ProofNet is the strongest natural next candidate: 185 validation and 186 test
rows are bundled with DeepSeek-Prover. Its university-level definitions and
library knowledge differ from the arithmetic/competition training emphasis.
Use validation to test feasibility and freeze the test decision before viewing
test results. Audit formalization validity and imports first: the first local
holomorphic-function examples omit a connectedness assumption, illustrating
why the exact port matters. All conditions need identical validated statements,
contexts, sampling and verifier budgets.

## Decision sequence

1. Finish the already-running C2 evaluation. Compare C0/C1/C2/C3 at equal
   attempt budgets: success curves, base-solved theorem losses, base-mode
   recovery, concentration, and coarse strategy/lemma use. Review representative
   proofs from both directions, with theorem and length matching.
2. Test the existing checkpoints on ProofNet validation before training on a
   deliberately narrowed dataset. A concrete motivating hypothesis is that
   competition training shifts probability away from library/abstract proofs.
   If base cannot solve enough validation problems, this test has a floor
   problem; if GRPO improves, the proposed forgetting failure is absent there.
3. To distinguish C5 from C2, complete the matched no-exploration control and
   C5 under the same training recipe. The desired evidence is a target-domain
   loss under matched GRPO, smaller loss under C5 than C2, and acceptable source
   performance. Report ordinary pass@k over all target theorems as primary;
   use independently sampled base-support strata to investigate retention.
4. If C5 only changes syntax or loses to C2, retire generic retention superiority
   as the application claim. A narrower application could enforce a real
   deployment restriction (unavailable lemma/tactic or verifier budget), where
   rejected routes demonstrably fail under the target constraint. This would
   need a new, explicit experiment and blocking representation.

Do not choose the final benchmark or exclusion taxonomy by maximizing the
observed C3-minus-C2 gap. No new training, evaluation allocation, verifier
modification, or iterative blocking campaign was launched in this audit.

## Symmetric training-support recovery audit (September 12)

Exploratory hypothesis, stated before analysis: C3 might recover a complementary
subset of base patterns absent from C1 even if C2 has greater total diversity.
Using the finalized training loader on the C1/C2/C3 runs above (first 32
proposals per theorem, identical 9,655-theorem sets), intersect C0 archive
patterns absent from C1 with each method's observed correct patterns:

| Minimum C0 observations | Absent C1 | C2 only | C3 only | Both | Neither |
|---:|---:|---:|---:|---:|---:|
| 1 | 54,330 | 9,083 | 4,227 | 8,304 | 32,716 |
| 2 | 16,515 | 4,019 | 1,751 | 5,404 | 5,341 |
| 4 | 4,931 | 1,254 | 430 | 2,470 | 777 |
| 8 | 1,140 | 278 | 56 | 734 | 72 |

Each row partitions theorem-specific tactic signatures, not conjectures or
semantic proof ideas. At C0 count >=4, C3-only patterns occur on 409 theorems,
and C2-only patterns on 1,118 (these theorem sets need not be disjoint).
C2 recovers 3,724 patterns in total versus C3's 2,900 on that stratum.
Thus there is sampled complementarity, but this audit favors C2 even for
repeated base support; it does not support a C3 retention-superiority claim.
Absence in 32 samples does not prove forgetting. These are evolving-policy
training samples, not final-checkpoint held-out evaluation. C1 also differs
in optimizer settings. No inference about C5 reward rejection follows.
