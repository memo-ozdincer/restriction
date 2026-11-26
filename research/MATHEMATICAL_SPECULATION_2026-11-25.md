# Mathematical speculation: oracle insight screen (Codex CLI)

User requests the first experiment on difficult-ish math, Luna Low vs Terra
High, escalating Sol Medium, Sol 6.2 Medium, Astra 6.2 Medium only if insufficient
performance gap. This is an isolated natural-math pilot, not a change to the
historical Lean RLVR baseline. Local project preflight reports missing cluster
CUDA/Lean environments. The experiment uses eight exact-answer tasks with
independent deterministic computations; **answer correctness is not Lean-verified
proof correctness**. Mathematical reasoning and supplied facts will be audited
separately; no claim of certified proofs or speedup.

## Prospective hypothesis and frozen panel

Hypothesis: on a domain/instance where a stronger model succeeds and Luna fails,
one non-answer mathematical discovery communicated from the stronger model's
own successful reasoning can unlock independently generated solutions from Luna.
A plain true but uninformative statement controls for the existence of an extra
hint. Compare the success gap, recovery conditional on baseline failure, and
teacher/student reasoning similarity descriptively. No training/fading here.

Eight fixed diverse discrete/number theory/probability problems in
experiments/mathematical_speculation_20261125/panel.json. Exact independent
answers calculated by reference.py; the candidate models do not see either
reference computation or answers, one isolated fresh CLI session per root/arm.
No tools, browsing, external files, code execution or other agents during math
generation. Read-only isolated cwd, no project instructions or prior sessions;
log all tool events, invalidate any session using them. Output JSON with exact
answer, concise mathematical derivation, one intermediate mathematical discovery
and its justification (all arms same response format). Teacher's insight must
be an independently checkable claim/relationship, not entire proof, final answer
or a trivial restatement; audit and freeze eligible teacher objects prior to
hinted generations. No known-answer or teacher reasoning text supplied to student
beyond the selected insight. Report ineligible cases without replacement.
Control hints are prewritten true facts in panel; their informativeness and
length may differ, so treat as auxiliary rather than a matched semantic control.

Teacher ladder frozen from user instruction: gpt-6-luna/low fixed student;
gpt-6.1-terra/high, then gpt-6.1-sol/medium (interpret 'sol medium' as
same-generation Sol), gpt-6.2-sol/medium, gpt-6.2-astra/medium. Stop at first
teacher whose exact answer total exceeds Luna by at least 2/8 and whose
correct answers include at least two student failures. If none, retain
all data; do not invent new tasks or more samples to manufacture separation.
One rollout per model/root/condition (not statistical generalization).
Only use teacher-correct cases with validated non-answer insights, both
student-correct and student-failed, for paired hinted/control arms; report
the complete panel and all exclusions. Compare normalized textual proof
steps descriptively and inspect whether the mathematical relationship was
used; not a claim of semantic similarity on an automatic metric.
No actual dynamic speedup measured: teacher solutions already generated.
Time/token usage is evidence for a future budget proposal, not an acceleration
result. Model revision as advertised by CLI, not underlying weights.

Run artifact directory: research/experiments/mathematical_speculation_20261125.
CLI version, model IDs, effort, prompts, model response output, JSONL event
logs and timings preserved separately. No hardware allocations or training.
