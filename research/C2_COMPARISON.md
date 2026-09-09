# Rewarding-the-Unlikely comparison

Last updated: 2026-09-09

## Question

Does Restriction-RL's persistent hard exclusion preserve a broader useful
correct proof tail than the released Rewarding-the-Unlikely soft rank penalty
when the model, optimizer, theorem order, seed, proposal budget, verifier, and
evaluation panel are matched?

This comparison stress-tests two parts of the novelty claim:

1. whether C3 improves over an explicit exploration method rather than only
   over ordinary GRPO; and
2. whether persistence and hard exclusion add value beyond generic pressure
   against high-likelihood correct samples.

## Mechanism contrast

| Property | C2 soft unlikeliness | C3 Restriction-RL |
|---|---|---|
| Novelty proxy | Current-policy sequence likelihood rank | Frozen C0 tactic signature |
| Scope | Every sampled group with usable reward variation | 1,014 archive-eligible theorems |
| Memory | Recomputed within the current rollout group | Persistent across all training steps |
| Intervention | Multiplicatively reduce high-likelihood correct rewards by up to approximately 24% | Set the archived dominant correct mode's final policy advantage to zero |
| Alternative correct proof | Relatively up-weighted after group normalization | Receives the ordinary positive signal |
| Incorrect proof | Reward remains zero | Upstream treatment unchanged |
| Restart | Pristine base in the registered comparison | Pristine base |

C2 is adaptive: a solution is penalized only while it ranks as relatively
likely in its current group. This can produce the self-correcting diversity
recovery described in the paper. C3 is deliberately asymmetric: the single
dominant C0 mode stays blocked even if its probability later falls, while an
unarchived mode is never blocked merely because it becomes common during C3.
The comparison therefore tests persistent displacement of a known base-policy
mode against continuous local rebalancing.

## What the published C2 result establishes

The bundled authors' notebook contains the exact values behind the paper's
main `Dval` figure. On its 200-theorem panel, GRPO-Unlikeliness-2 changes the
pass@N curve relative to GRPO-Default as follows:

| N | GRPO-Default | C2 soft unlikeliness | C2 minus default |
|---:|---:|---:|---:|
| 1 | 70.97% | 65.49% | -5.48 pp |
| 2 | 74.29% | 72.88% | -1.42 pp |
| 4 | 76.17% | 76.39% | +0.21 pp |
| 8 | 77.44% | 79.13% | +1.69 pp |
| 16 | 78.31% | 81.73% | +3.42 pp |
| 32 | 79.06% | 84.31% | +5.25 pp |
| 64 | 80.00% | 86.75% | +6.75 pp |
| 128 | 81.13% | 88.75% | +7.62 pp |
| 256 | 82.25% | 90.25% | +8.00 pp |
| 512 | 83.00% | 91.00% | +8.00 pp |

The paper also reports 8,065 of 9,600 training problems solved by C2, compared
with 7,860 by GRPO-Default and 7,707 by the static base model. Its qualitative
claim is that soft unlikeliness sacrifices probability at the shallow head,
crosses ordinary GRPO by roughly four samples, and continues accumulating a
substantially better tail.

This resembles C3's observed crossover against C1: on our combined
467-theorem panel C3 is 1.97 points below C1 at pass@1, 0.28 below at pass@4,
0.13 above at pass@8, and 0.43 above at pass@128. The shared shape makes C2 a
high-value comparator: both interventions may address the same rank-bias
failure, but apparently with different pressure at the head.

## Why the published numbers are not a direct C2/C3 result

The paper values above must not be numerically ranked against our C3 values:

- the paper's main `Dval` has 200 theorems, while our registered validation set
  has 223 and our combined panel has 467;
- the exact theorem identity relationship is unresolved;
- the paper generates 512 responses and reports chunked pass@N trials, whereas
  our deep result estimates pass@N from a frozen 128-response sample;
- the paper's diversity plot counts unique proof strings, while our primary
  measure is a deterministic ordered tactic-head signature; and
- the paper's final 11K recipe differs from our 9,655-theorem registered run.

The published result is therefore mechanism context and a qualitative prior,
not evidence that C2 beats or loses to C3.

## Frozen matched analysis

The new run uses C2 and C3 settings that differ only in the exploration
mechanism. The training panel reports:

- raw correct tactic modes and exact normalized proofs;
- paired theorem-level correctness, mode, concentration, and effective-mode
  changes;
- equal-correct-draw rarefaction through 32;
- chronological diversity trajectories;
- separate effects on C3 archive-eligible and ineligible theorems; and
- recovery by C3 of repeated C0 modes absent from C2.

The final checkpoint panel uses the same 467 theorems and 128 proposals as the
completed C0/C1/C3 evaluation. It reports pass@1 through pass@128, rarefaction
through 64 correct draws, all six frozen proof representations, and C0-mode
recovery relative to C2.

## Interpretation map

The following outcomes have different scientific meanings:

- **C3 wins primarily on archive-eligible training theorems:** supports the
  intended persistent dominant-mode mechanism.
- **C3 also wins on archive-ineligible theorems:** suggests transfer of
  exploration behavior across theorem families; this requires diagnosis and
  is not direct blocking evidence for those prompts.
- **C2 and C3 are within the 5% practical-null band:** soft adaptive weighting
  captures most of the benefit, weakening the necessity claim for hard
  persistence.
- **C2 has better pass@1 but C3 has better equal-correct tail coverage:** hard
  exclusion makes the stronger diversity/correctness tradeoff.
- **C2 has equal or broader tail coverage:** the hard mechanism is not superior
  and may be unnecessarily irreversible.
- **The direction changes across proof representations:** the novelty claim is
  signature-sensitive and must be stated at the resolution where it holds.
- **Both exploration methods beat a matched no-exploration control:** supports
  deliberate exploration generally. That final attribution still requires the
  separately paused matched control.

## Execution status

- C2 training job: `902537`.
- Dependency-bound C2 pass@128 evaluation and comparison job: `902538`.
- Both had zero runtime at registration.
- Trillium's H100/H200 nodes are currently covered by a maintenance shutdown
  reservation through 2027-09-08, so the jobs have no start estimate.
- The original Nibi cluster is reachable over the network but requires an
  interactive MFA login; no noninteractive credential is available in this
  environment.

No C2 scientific result exists until the complete training and evaluation
artifacts pass their frozen gates.
