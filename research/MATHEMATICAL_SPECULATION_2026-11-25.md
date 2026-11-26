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

## Baseline and teacher selection (before hinted arms)

Luna Low answers 1/8; Terra High answers 7/8, including six Luna failures.
All 16 CLI sessions returned valid JSON with no tool events. The registered
gap criterion passes; no escalation. Terra failed record_derangements and
its hint is excluded. Audit freezes seven eligible non-answer discoveries
and seven original control statements in the run directory. On pattern_race,
teacher's own gambler setup is appended to make its overlap insight
interpretable; no payout table or final equation is forwarded. The other
six are literally the teacher's stated insight. Several are already present
in Luna's unsuccessful reasoning; this is important rather than a reason to
replace them. The matched arm tests the supplied object as chosen, not an
oracle retrospectively tuned to rescue each error.

## Primary hinted result and discriminating follow-up registration

All 14 hinted/control sessions were valid and tool-free. The seven eligible
teacher-correct roots yield 1/7 Luna baseline, 1/7 Luna insight, 1/7 Luna
control answers. None of six Luna failures were recovered by either hint.
The sole answer-correct matrix task has an inconsistent baseline and control
derivation, while the insight arm's derivation correctly uses alternating
cycle counts (1440+600). Thus answer matching alone hides one useful
proof-quality effect. The primary gap is not closed.

The peer solutions often share a strategy but fail at exact execution: Markov
Vieta descent, cyclic run decomposition, grid spectrum, primitive triples
inclusion-exclusion are already present in baseline Luna; repeating a generic
fact is not genuinely new knowledge. On pattern_race Luna used an erroneous
Markov-state system and ignored the supplied gambler setup. This motivates a
specific follow-up alternative explanation: the self-reported insight was
too weak, not a test of a more useful intermediate discovery.

Freeze two sharper, teacher-derived non-answer objects: the exact path
Laplacian characteristic factor polynomial (grid_trees), and the stopped
fair-game expected-payout equality (pattern_race). Both are in Terra's
successful proof, neither gives final answer or evaluated pattern payouts.
Different mathematical content, not additional seeds or outcome-selected
reruns of the same hint. One fresh Luna rollout per task. Decision: can a
more precise teacher object replace the failed part of the student's approach?
No claim about prevalence or statistical power, no new teacher or panel.

## Final result

All 32 requested/diagnostic CLI sessions returned structured responses;
no shell, file, browser, or other tool run appears in their event streams.
The two sharper-hint sessions also fail. The exact answer scorer reproduces
all metadata in summarize.py; inspect strategy-audit.json for manual,
non-kernel judgments.

| Task | Correct answer | Luna | Terra | Luna + insight | Luna + control | Sharper object |
|---|---:|---:|---:|---:|---:|---:|
| Markov triples | 13 | 16 | 13 | 14 | 3 | — |
| Pattern race | 13/28 | 7/12 | 13/28 | 7/13 | 11/24 | 13/25 |
| Cyclic strings | 645 | 1056 | 645 | 40 | 20 | — |
| Record derangements | 43831 | 29334 | blank | — | — | — |
| Grid spanning trees | 30305 | 2415 | 30305 | 2415 | 2415 | 2415 |
| Ballot paths | 55054 | 7203 | 55054 | 68923 | 191790 | — |
| Primitive triples | 170 | 616 | 170 | 227 | 138 | — |
| Bipartite matrices | 2040 | 2040 | 2040 | 2040 | 2040 | — |

On the seven teacher-correct roots: teacher 7/7, baseline Luna 1/7,
insight 1/7, control 1/7. No rescue of the six baseline failures. Sharper
diagnostic 0/2. The sole Luna answer match (regular bipartite graph)
has a numerically inconsistent baseline derivation ending 272, and the
control ends 888. The true mathematical cycle count hint yields a correct
derivation, 1440 + 600 = 2040. This is a concrete proof-quality improvement
hidden by the answer metric, not a new theorem solved. No other Luna
derivation in these arms is complete and correct in the manual inspection.

### Similarity and computation

Six of seven teacher-correct tasks use the same high-level method in
baseline Luna as in Terra; six of seven in the insight arm and six of
seven in the control. This is a descriptive manual architectural
classification, not a claim of semantic equivalence. The frequent case
is knowing the basic method but failing the execution (enumeration,
binomial coefficients, exact modular counts, or coordinates).
The explicit teacher fact is already used in 4/7 Luna baseline solutions
and 6/7 insight solutions. Pattern race's initial hint is ignored; the
sharper hint moves Luna to Terra's stopped-gambler method, but Luna
miscounts string overlaps and gives an incorrect result. In grid_trees,
even the supplied exact characteristic factor polynomial fails to
close the gap: Luna evaluates the polynomial incorrectly and its prose
ends 17280 while answer field remains 2415. This suggests the performance
gap on these tasks includes calculation and local execution, not merely
access to an important missing fact.

Median per-session CLI elapsed times: Luna baseline 10.48s, Terra High
16.05s, Luna insight 10.54s, Luna control 9.58s. Actual tool/API usage
recorded in each metadata file; reasoning-token counts were 0 for Luna
and 4,382 total for Terra. These are joint model/effort comparisons,
unknown model parameter sizes. CLI overhead and parallel execution mean
elapsed values are not intrinsic hardware latencies; no end-to-end
hybrid speedup is claimed. Answers are exact-checkable but proof quality
is manually reviewed, not actual Lean-verified. This eight-root pilot
is not a distribution-wide estimate.

Conclusion: identical high-level reasoning strategies are available
before hints but do not consistently support correct calculations at
Luna Low. The specified mathematical discovery offload does not
materially close the 6/8 exact-answer gap on this panel. We preserve
the concrete alternating-cycle improvement and pattern method switch,
but do not escalate teacher or repeat this null simply to generate
a positive result. The dynamic acceleration hypothesis remains open,
not supported by this first pilot.
