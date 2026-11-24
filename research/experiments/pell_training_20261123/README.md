# Can a learned Pell construction transfer?

The prior matched trial obtained a valid deeper solution only when the experiment executed the forward map. Train two small LoRA adapters independently from final C1, comparing demonstrations that express the multiplication of a fundamental unit and a current unit against demonstrations with the identical resulting coordinates multiplied out. Same eight training prompts, verified witnesses, optimizer, order, seed, four epochs, 32 update steps, response-mean likelihood and reference anchor. Token counts may differ between mathematical expressions and numerals and are recorded. This is supervised training on a GRPO checkpoint.

Use D = 2,3,5,7 for training. For each D, require a witness outside the first two or three absolute coordinates, supplying the fundamental unit and most recent excluded unit. Test D=6 and D=10 at the next-after-third level, with (i) familiar coordinate names, (ii) renamed and reordered declarations, and (iii) only the original bare equation and forbidden values. Also check the easier D=6 next-after-second case with named coordinates. Neither evaluation discriminant appears in training. No correct test coordinates appear in the prompts. Treat the training examples as authored scaffolding and distinguish syntactic template reuse from scaffold-free generation.

Evaluate C1 and both adapters with 16 shared-seed proposals per cell, temperature/top-p one, cap 256. Primary descriptive question: does expression supervision improve fresh verified completions over both controls on each of the two named third-level tasks? Report renamed and bare performance even when negative. A result that disappears on renaming identifies a different limitation than a result that survives renaming but disappears without supplied coordinates. One run, no checkpoint selection.

## Prospective interface ablation after the main result

The expression-trained adapter passed 15/16 and 13/16 deeper held-out draws with the familiar names and passed 0/16 on both when names and declaration order were changed together. Cross the two missing conditions: rename alone in original order, or reorder alone with original names. Use the saved expression adapter with response log-probability reload readback, both held-out discriminants, 16 draws each, and identical seeds to the original named/renamed cells. No retraining. If only one manipulation reproduces the collapse, that isolates its effect under this tested scaffold.

## Verified results

Both control policies scored zero on all seven cells. With familiar names and order, expression supervision produced the same multiplication formula for 15/16 deeper D=6 attempts and 13/16 deeper D=10 attempts. The corresponding coordinates are (485,198) and (27379,8658). The easier D=6 task yielded 16/16. Both bare tasks and both renamed-and-reordered tasks yielded zero. Each accepted named proof used the training formula and let Lean evaluate the new inputs.

| Declarations | D=6 | D=10 |
|---|---:|---:|
| Original names and order | 15/16 | 13/16 |
| Renamed only | 0/16 | 0/16 |
| Reordered only | 2/16 | 14/16 |
| Renamed and reordered | 0/16 | 0/16 |

The crossed check used the reloaded adapter, unchanged values and paired seeds. All 400 generated responses were reconciled to their Lean sources or parse outcomes. This single-seed supervised pilot matched optimizer steps and demonstrations. Expression supervision used 1,696 response tokens versus 1,084 for literal supervision.

Both adapters, raw training records and 336 main evaluation attempts are in the [verified GitHub release](https://github.com/memo-ozdincer/restriction/releases/tag/pell-training-2026-11-23). The 64 crossed-condition responses are in name-ablation/.

The separate crossed-interface auditor reconstructs all four prompts, paired
seeds, 64 source mappings and 32 unique Lean checks; no verdict is unresolved.
Adapter reload discrepancy is zero. Job 1399296 released its H100 after 5m58s.
The result demonstrates transfer of a supplied multiplication formula to new
numerical inputs with a familiar interface. It does not demonstrate discovery
of that formula, reliable identifier-independent abstraction, or autonomous
solution generation from a bare equation. The main and crossed outcomes are
kept together so the successful numerical transfer cannot hide those limits.
