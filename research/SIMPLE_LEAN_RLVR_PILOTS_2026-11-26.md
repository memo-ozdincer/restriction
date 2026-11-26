# Simple single- and multi-agent Lean pilots

User direction, verbatim:

> forget about very intricate designs, just keep trying luna low, medium and terra low and medium in single and multi agent experiments.
>
> Send some subagents to suggest the experiments that preserve the magic of RLVR

Three independent critiques converged on native feedback/restart, free proof
relay, and unrestricted consultation. These are inference probes for eventual
terminal-only RLVR, not evidence of training or gradient transfer.

## Ranked experiments

1. **Same-model retry versus restart.** First full proof, then on failure
   either feed exact failed attempt plus raw Lean output to the same model or
   make a fresh direct attempt. Both may completely replace their proof.
   Question: is accumulated native information useful beyond independent
   sampling, or does it anchor the model? First run registered in
   [lean_retry_20261126](experiments/lean_retry_20261126/README.md).
2. **Cross-model relay.** Receiver sees original theorem, failed proof and
   raw Lean output; can freely revise or replace. Paired receiver alone and
   same-model retry controls. Question: is useful partial reasoning more
   transferable across settings than within one setting? Pick pairings based
   on observed failure patterns, not a larger arbitrary grid.
3. **Ask anything.** Actor can prove directly or ask a partner any question;
   partner responds without a fixed mathematical role; actor submits final
   proof. Whole-goal delegation legal. Compare against independent attempts
   with the same role/call budget; self-dialogue is a useful distinct control
   after a positive mixed-pair result. Question: does model-selected help
   overcome the previously observed consumption bottleneck?
4. **Self-plan then execute.** Same model generates a free mathematical plan
   before executing, versus two independent direct proof attempts. Lower
   priority: requires explicit plan generation, so tests a deliberately
   restricted interface rather than fully endogenous decomposition.

## Minimal magic-preserving rules

- Luna Low/Medium and Terra Low/Medium only, no stronger escalation.
- Exact original theorem and native Lean verification; reward only complete
  accepted proofs. No human ratings, forced invariants, predefined handoff
  locations, mandatory reasoning decomposition, rejection of full-goal help,
  or reward for intermediate success. Allow replacement of earlier reasoning.
- Charge all calls, verification and actual usage; equal calls are not equal
  FLOPs. Preserve all failures. Analyze what went wrong after the experiment,
  not as a filter determining which proof deserves credit.
- Small fixed panels with a predeclared question; no blind scaling or chasing
  a significant result. Treat model-dependent effort settings as such, not
  known parameter sizes. Inference studies do not establish learning.
