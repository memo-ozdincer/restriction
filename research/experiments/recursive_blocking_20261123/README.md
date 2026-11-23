# Recursive blocking pilot

Before examining the second half of the C0 rollouts, test whether a third tactic signature survives two successive exclusions on training theorems. Use the first 16 of the registered 32 proposals per theorem for selection. Require a unique leader with at least two occurrences and at least 40% of remaining correct proposals at each of the first two rounds, and at least two correct proposals remaining after both exclusions. Freeze eight eligible theorems by ascending SHA-256 of theorem name. Use the second 16 only to estimate available alternatives and inspect actual proof bodies. This offline measurement establishes a baseline for a matched online GRPO comparison. An interesting online result would be a verified alternative using a different mathematical argument, beyond changes in tactic order or wrappers.

## Held-out diagnostic specified before splitting the logs

Within miniF2F test and registered validation separately, split each model's 128 existing proposals in saved order into 64 discovery and 64 confirmation draws. Select problems solved exclusively by one policy in discovery. Ask how often that same directional advantage repeats in confirmation, and do the symmetric calculation for GRPO. Report all four outcomes, including neither and tied successes. This checks sampling stability within one training seed. It does not estimate the result of a second training run.

## Results

- The training-only screen found 705 eligible theorems among 9,655. In the frozen eight, 113/128 confirmation proposals were recorded correct. Excluding one discovery signature leaves 75, and excluding both leaves 48 across all eight theorems. These are previously generated proofs. In problem 42013, both excluded signatures and the surviving examples use essentially the same completed square. On 11649, the two excluded proofs and the surviving example all choose the empty sets. A tactic-signature count alone would misclassify these as discoveries.
- On miniF2F test, two roots were solved exclusively by C3 in the first 64 proposals. One recurred in the second 64 (numbertheory_notequiv2i2jasqbsqdiv8, 1 then 3 accepted versus GRPO 0 then 0). The other had no second-half successes for either model. Neither of the two C3-exclusive validation roots repeated exclusively. Neither split had a first-half GRPO-exclusive root. Across the whole test panel C3 gained two net roots out of 244 at 128 draws, with a 1.76 percentage point lower pass@1.
- The recurring theorem has a simple counterexample: 2 and 0 are even but their squared sum is 4. A literal integer-pair scan of generated proofs detects a mathematically valid counterexample in 64/128 GRPO proposals and 57/128 C3 proposals. Lean accepts zero and four respectively. The base and soft-unlikeliness runs also solve it (1 and 3). The evidence points to a difference in completing a proof once a witness appears. The scan matches a subset of syntax and does not establish that every detected pair was used as intended.
- In the separate compiler-credit experiment, mapped supervision solved all eight invariant roots (71 accepted samples) and no other composition roots. Full supervision solved the same eight (121) plus three witness roots (8). An accepted example on each of those three constructs coefficients from the preserved determinant and explicitly supplies them to the witness lemma. This suggests a miniature test of witness selection versus verified proof completion.

Next online comparison: measure ordinary GRPO against recursive blocking with fresh on-policy proposals, using training-only dominance updates. Keep the matched proposal budget and report both theorem transfer and the actual witness or mathematical certificate. Reserve the inspected mod-8 theorem for diagnosis.

## Prospective online protocol

A shared discovery actor receives one ordinary GRPO pass on the eight frozen problems. A fresh 16-proposal group per problem then sets the first blocklist. Both comparison actors restart from the same pristine base with zero-initialized LoRA output, the same optimizer, sampling seeds and task order. They train for two passes, 16 on-policy samples per task per pass. After the first pass the recursive actor may add one previously unblocked signature per theorem. Promotion requires a unique leader with at least two occurrences and 40% of remaining correct samples. Mask only verified correct matches and skip an entirely blocked success group. Skip zero-variance groups in both arms.

After training, probe each training problem and four prospectively written related transfer problems without applying any exclusion. Use equal 256-token generation limits and Lean checks across arms. Record all outputs including parse failures and skipped updates. Primary descriptive outcomes are accepted samples and solved tasks on transfer, and verified proofs on the training probe whose mathematical witness or argument differs from the excluded examples. Compare individual proof bodies. This is a one-seed, two-update-pass pilot, with related-task transfer measured separately from historical miniF2F results. The source freezes the transfer statements.

## Online outcome

Job 1398215 finished all 72 groups on one H100 in 31m44s including allocation setup. Discovery promoted five signatures. The recursive arm added five more after its first pass, with four problems reaching depth two. Both comparison actors updated 14 times. Exclusion removed 29 correct proposals from the first pass and 36 from the second. All 120 corresponding adapter tensors differed between the final actors.

| Fresh probe | Ordinary GRPO | Recursive blocking |
|---|---:|---:|
| Training problems solved | 8/8 | 8/8 |
| Accepted on training probes | 104/128 | 102/128 |
| Accepted outside the same final archive | 52/128 | 53/128 |
| Transfer problems solved | 4/4 | 4/4 |
| Accepted on transfer | 45/64 | 45/64 |

Matched seeds produced identical response tokens on 124/128 training probe pairs and 63/64 transfer pairs. Square, weighted cube, absolute value and finite-set transfer yielded respectively 1, 15, 13 and 16 successes per 16 draws in both arms. The only changed transfer response adds a second nonnegativity hint. All four Lean ablations under the same tactic show the first hint alone succeeds and the second alone fails. On the quartic training problem, two control successes became failures. With the control proof's simplification fixed, removing either of its two square hints breaks that proof. On the empty-set training problem every sampled proof body was identical across arms. The observed extra training-probe success outside the archive is too small to support an advantage in mathematical discovery.

This pilot used LoRA, one seed, two training passes, and four related transfer tasks. The common random draws expose small changes in behavior efficiently. These results leave longer-run behavior and broader transfer unmeasured. A useful follow-up would ask whether excluding a *verified sufficient certificate* changes witness choice where excluding its tactic wrappers did little.

The audit reconstructs all 1,152 proposals, blocklist updates and outcomes from saved tokens/text, code and Lean verdicts. The release holds all three adapters and the raw records. The downloaded archive and all 241 members matched their checksums. [GitHub release](https://github.com/memo-ozdincer/restriction/releases/tag/recursive-grpo-2026-11-23)
