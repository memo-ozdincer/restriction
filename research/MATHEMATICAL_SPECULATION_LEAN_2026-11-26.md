# Corrected mathematical speculation pilot: actual Lean formal verification

User correction: the previous natural-language exact-answer exercise was
not a Lean experiment. Retain it as a separate diagnostic and do not
interpret it as formal proof competence. User also authorizes Luna Medium.

Hypothesis: if smaller models discover correct ideas but fail to implement
them formally, a stronger model receiving only those ideas may successfully
implement them, while receiving a verified mathematical intermediate from a
stronger model tests the reverse direction. This could inform an eventual
routing mechanism, not merely more attempts. No RL training.

## Environment

Locally installed exact historical Lean 4.9.0-rc1 Darwin-arm64 release.
Read-only transport of a transitive compiled Mathlib subset from the user's
pinned Trillium project (revision 2f65ba7f1a9144b20c8e7358513548e317d26de1).
The smaller import header is a genuine difference from the historical
whole-Mathlib verifier; freeze it for all arms and recheck known positive
witnesses. Fresh native Lean process, 60s timeout, original statement and
allowed axioms propext/Classical.choice/Quot.sound; no stub/sorry acceptance.
No cluster job or model weights required.

## Panel

Hash-rank MiniF2F test theorem names with C0 1–12 correct out of 128 (historical
difficulty proxy). For each candidate root try first at most three archived
correct proof bodies under the exact local header; freeze first eight roots
with a verified witness. Record all attempts and exact source hashes.
Witnesses never appear in candidate model input. This is held-out from
our project training archive, but not necessarily model pretraining.
No selection using new Codex results. The selection is import-compatible,
not a population-random sample. No change to historical experiment.

## Arms and prospective decision

One independent tool-free Codex CLI session per question and baseline:
gpt-6-luna low, gpt-6-luna medium, gpt-6.1-terra high. Model returns a
brief informal idea separated from Lean tactic proof body (no answer-only
scoring). Additionally asks for optional root-context intermediate mathematical
claim and proof, if a useful one is actually used in the derivation. Every
proof body must be checked as the original theorem by native Lean. Never
send reference witness or a failed student's proof to teacher.

Choose primary Luna tier Low unless Medium shows a more informative
intermediate capability (at least two additional verified proofs and at
least two Terra-only solves); label both tiers individually. Teacher
escalation only if Terra verified solve total exceeds Luna Low by fewer
than two AND has fewer than two exclusive solves; user ladder unchanged.
After baseline, freeze all proposed student ideas as emitted, including
mistaken/unclear ones. For each unresolved student proof, independently
ask Terra to execute only its idea (and original theorem/header); no
student proof body, error messages or teacher solution. Compare against
Terra ordinary baseline on same roots, audit whether idea was actually
used, track total output/reasoning tokens and elapsed costs. Optional
reverse insight arm: validate teacher's proposed root-local claim via
native Lean with known reference proof as final closure; only if proven
and not merely identical to root/assumption, furnish its type as an actual
local h_help to Luna, with teacher proof term hidden. Verify entire
assembled proof. Record unavailability, do not fabricate lemmas;
the assessment is matched terminal correctness not a PRM. No model trained.
All runs use same imports, prompt tool restrictions and verifier.

Environment correction before any candidate generation: the selective Mathlib
header does not load the Topology namespace. Positive fixture failed on that
header despite ring closing its own goal; remove only the unavailable namespace
open, preserve the rejected fixture and partial witness checks. Panel selection
restarts before any Codex model rollout. This is an import-environment correction,
not verifier relaxation.

## Baseline and frozen handoffs

All 24 model runs returned valid, tool-free output. Lean Low 0/8, Medium
0/8, Terra High 4/8. No escalation necessary; primary student remains Low.
The Low idea-only arm includes all eight rejected proofs without selection on
idea quality. Medium's proof score is unchanged but the mathematical plan
changes on three informative roots: factorial divisibility (false factorial
bound vs recognizing prime factor 17), common quadratic roots (incorrect
difference factorization vs root values 2 and 3), even factors (unbounded
nonlinear omega vs finite enumeration). Freeze these three Medium handoffs
as a distinct effort/strategy diagnostic, not additional replicas.

The reverse fact audit initially concatenated the known witness with an
extra indentation level after clear h_help, yielding a syntactically invalid
continuation. Preserve failed sources and outputs; dedent the unchanged witness
before concatenating and reverify. No pilot model is queried in this correction.
Facts can be eligible even when Terra failed the full theorem, provided their
actual root-context proof separately passes the unchanged kernel/axiom audit.

## Idea-only handoff result and final efficiency diagnostic registration

Low→Terra (only the student's emitted idea + original theorem) 4/8, same
accepted root set as Terra direct 4/8. Teacher output tokens 7,007 vs 8,362
(-16.2%), reasoning tokens 4,253 vs 5,073, summed generation time 161.31s
vs 185.40s. But generating the student full proofs and ideas cost 1,466
extra output tokens and 60.70s, so these measurements do not establish a
hybrid speedup. Medium divergent ideas 2/3, same accepted roots as low
and Terra direct on that subset. Three native Lean-verified teacher
hypotheses supplied to Low yield 0/3, despite actual use of the facts.
These findings motivate one distinct efficiency diagnostic: generate **only
the mathematical idea** with Luna Low (no attempt at a Lean implementation)
on the same eight roots, then Terra implements the idea using the same
frozen execution prompt. Compare actual summed two-model generation tokens,
reasoning tokens, summed sequential generation/verification times, and
verified accepted roots to Terra direct. The new role avoids the redundant
student proof attempt cost; this is not another seed of the full-proof
condition. No direct speedup claim unless matched resource accounting shows it.
