# Experiment 1: matched versus swapped unrestricted HELP

Registered before any CLI generation. Hypothesis: the actor's freely selected
question elicits assistance especially useful to its own mathematical path,
beyond the same partner's unrelated response to another actor on the exact
same theorem. Swapping exchanges controls for the answer bank rather than
asking humans to decide which mathematics matters. A swapped advantage may
indicate anchoring/misdirected questions; ties do not establish equivalence.

Use the first four hash-ranked roots of the prior frozen MiniF2F panel,
identical pinned Lean 4.9.0-rc1 and selective Mathlib header. Two independently
sampled actor attempts per root for each pair Luna Low→Terra Low and Luna
Medium→Terra Medium. Actor can submit a full tactic proof or ask ANY question
(including a whole-solution request), optionally expressing its own work in
its message. No forced question or intermediate object; no resampling to get
requests. Verify every submitted proof. Partner sees exact goal and entire
question and responds freely; no correctness filter, no predefined roles.

For each actual question, freeze one partner reply. Fresh continuation receives
its own exact initial question, and either (a) its matching full Q&A exchange,
(b) the other question's full Q&A exchange (only if both actors asked), or
(c) no partner response. Same prompt template, actor model, effort and root;
no statements that the supplied exchange is good or bad. The initial question
is retained in every condition. Present complete Q&A together to reduce
broken notation/pronoun confounds. The only scored output is a complete Lean
proof checked in the unchanged verifier. Compare paired outcomes on units
where both asked and both reply calls valid; other questions still get
matched/no-help if partner output available, separately reported. All direct
actor proofs and failed/invalid responses are preserved; no replacements.
Count hypothetical condition-level first/partner/final calls and actual
physical calls, tokens/time; shared partner bank reused across counterfactuals.
No-help is a same-history continuation control, not equal model-call compute.
At most 80 CLI calls (16 actor + 16 partner + 48 continuation). One draw per
prefix/condition; no fixed CLI seed. No learned reward or model update.
Post-hoc characterize objective overlap, whether final proof incorporates a
reply, and full theorem delegation; do not filter by usefulness. Matched gain
means question-specific usefulness, not proof of hidden state matching,
novel mathematics, or actual RL learning.

Local training preflight fails CUDA/Ray/cluster dependencies as expected;
this is an isolated inference probe, existing native verifier unchanged.
