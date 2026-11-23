# From a collision key to a verified proof

Compare the final recursive-GRPO adapter with itself under paired seeds. The main task is the strengthened 42-element complement theorem with nonempty, disjoint witnesses. The hint supplies the collision key in a Lean comment. It supplies no proof code. The second task isolates conversion of a collision into equality of squared sums. Its hint supplies the pointwise identity that lifts to finite sums. Use 16 samples per cell, at most 2048 response tokens for the main theorem and 512 for the bridge. Record parsing, token-limit hits, raw Lean errors and verified acceptance separately. No training or adaptive selection. A positive bridge with a failed root would localize an available proof component; a tie on the root would not establish which remaining component caused failure.

## Run checkpoint

Job 1398627 used one H100 on trig0050. At checkpoint, 4 of four sample groups had complete raw records. The checkpoint preserves the prompt, response tokens, model text and sampling seed for each saved group. Check the final audit before interpreting model outcomes.

## Final audit

All 64 proposals were recovered. Lean accepted 0/16 in each of the four groups. The complete-theorem responses all parsed and stopped before the generation cap. Two bridge responses failed the parser; the other 62 proposals across tasks produced 50 distinct Lean sources. Every submitted source received a resolved verdict. The saved prompt, response body, source hash and corresponding verdict were reconciled for each proposal.

Both authored positive controls passed, and both negative controls failed. Supplying the collision key did not yield a complete proof in this sample. Even the isolated bridge remained unsolved after giving its pointwise identity. The paired first root response chose B and the empty set in both conditions, violating nonemptiness. This is one adapter on two tasks. The allocation released after 5m36s.
