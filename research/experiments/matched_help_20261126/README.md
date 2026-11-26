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

## Primary result and registered follow-up

All 16 valid, tool-free initial actors independently selected `proof`; all
16 rejected in Lean. No HELP request or partner call occurred, so matched
versus swapped is unidentifiable in the primary arm. This is informative
about spontaneous routing in the zero-feedback initial decision, not proof
that help is ineffective. Do not include generated questions as primary
spontaneous requests.

**Separate failure-conditioned request-content diagnostic**, registered now:
all 16 failed first attempts (two per setting/root) are reused. Show each
actor its own exact proof and raw Lean rejection, then ask it to choose any
question to send to its assigned partner, including requesting the complete
proof. This one extra stage is mandatory, but WHAT is communicated is fully
actor-selected; no claim about spontaneous choice to request help. Partner
sees original theorem and exact question and answers freely. Freeze each
answer; replay the same actor history (failed proof, raw diagnostic, own
question) in matched exchange, swapped whole Q&A, and no-response control.
All final attempts use unchanged Lean validation. Counterfactual partner
bank reuse and actual costs logged; control retains own question and error,
so measures incremental response benefit beyond self-diagnosis rather than
strict resource-matched superiority. No replacements. The paired diagnostic
identifies question-specific usefulness at a failure checkpoint; it tests
content selection, not call routing. Up to 80 additional sessions.

Infrastructure audit while diagnostic ran: four partner sessions returned
complete valid structured replies after WebSocket-to-HTTPS fallback, whose
informational CLI `error` item was incorrectly counted as tool use. Preserve
original metadata, accept only this precisely identified transport fallback
when the same response completed successfully with no actual tool events,
and complete previously skipped counterfactual continuations using those
unchanged replies. No regenerated partners or outcome-based selection.
The original runner's in-memory eligibility remains unchanged while it
finishes; audit and fill missing arms afterward. This is an event-type
classification correction, not a changed proof validity criterion.
