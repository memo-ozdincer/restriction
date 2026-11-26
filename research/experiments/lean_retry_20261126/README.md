# Native feedback versus independent restart

Registered before sampling. Hypothesis: a rejected proof and raw native Lean
feedback expose productive paths that a fresh resample does not, potentially
differently across Luna Low/Medium and Terra Low/Medium. Use the first four
hash-ranked roots of the existing frozen MiniF2F panel (no selection on new
outcomes). For each setting generate one direct proof and check with unchanged
pinned Lean and selective Mathlib header. Only on first failure, make two new
calls of that same model/effort: one with the exact previous candidate and
raw verification output, one with identical original prompt alone. Both may
replace the entire proof. Count all calls and only terminal kernel acceptance;
compare paired outcomes on the same failed first attempts. No intermediate
reward, forced mathematical strategy, human correction, or new training.
Record actual tokens/time, not claim exact compute equality. No extra repeats.
This step tests single-agent feedback before cross-model relay. The existing
verifier remains unchanged. One draw per setting/root/arm; no CLI seed.

## Results

44 valid, tool-free sessions: 16 first attempts and 14 matched failed-first
pairs (28 second calls). All correctness verdicts from the pinned kernel.

| Setting | First | Feedback after failure | Restart after failure | Final with feedback | Final with restart |
|---|---:|---:|---:|---:|---:|
| Luna Low | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| Luna Medium | 1/4 | 1/3 | 0/3 | 2/4 | 1/4 |
| Terra Low | 1/4 | 2/3 | 1/3 | 3/4 | 2/4 |
| Terra Medium | 0/4 | 3/4 | 2/4 | 3/4 | 2/4 |
| Total | 2/16 | 6/14 | 3/14 | 8/16 | 5/16 |

Paired outcomes: three feedback-only, three both, eight neither, zero
restart-only. Feedback-only cases are Luna Medium factorial and Terra
Low/Medium quadratic roots. All three literally preserve the first proof's
mathematical structure, changing only one tactic or lemma qualification:
`norm_num` to `decide` for Nat.Prime 17, and `mul_eq_zero.mp` to
`_root_.mul_eq_zero.mp` for the real-root problem. Blind restarts repeat
exactly the same kind of error. These are native feedback-mediated recoveries,
not new mathematical discoveries. Both Terra results concern the same root;
do not treat 14 pairs as independent mathematical tasks. Luna Low never
recovers, despite receiving the same kind of native diagnostics.

Second-call aggregate: feedback 3,277 output tokens, 131.0 summed generation
seconds; restart 4,544 output tokens, 171.1s. Shared first calls use 5,912
output tokens, 191.0s (rounded). Both full two-stage pipelines charge the same
first stage. Time and token accounting are descriptive, not equal FLOPs.
No new RL or unassisted capability gain demonstrated. The result motivates
cross-model relay specifically on failed Luna Low traces, testing whether a
receiver can exploit them beyond its own attempt. That is a separate test.
