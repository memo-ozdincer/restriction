# Does an executable change of coordinates unlock the next Pell witness?

> Interface qualification (November 24): the standalone C1 experiments used a
> leading BOS marker and omitted C1's trained proof-boundary BOS. Recorded counts
> remain valid under those prompts; they do not establish native-interface
> capability limits. See the [confirmed audit and controlled comparison](../../PROMPT_BOUNDARY_2026-11-24.md).

Previous trials on the frozen C1 checkpoint found (5,2) readily. After excluding absolute first coordinates 1 and 5, both the raw problem and a verbal recurrence hint had zero verified samples. Test whether changing the coordinate in which the prover supplies a witness lets this same proposal prove the strengthened theorem.

Use the integer maps F(u,v)=(5u+12v,2u+5v) and G(u,v)=(5u−12v,−2u+5v). They are inverses and preserve the Pell norm. Score the input norm and exclude the absolute first coordinate of the decoded pair. The forward and inverse prompts differ only in one sign. A familiar positive seed maps to a permitted solution in one direction and a forbidden solution in the other; the reflected seed can reverse that. Both coordinate problems have exactly the same attainable decoded witnesses.

First freeze the prior 16 plain-2 and 16 blocked-2 proof bodies and cross them with direct, forward and inverse statements. Then generate 16 fresh attempts each under four interfaces with a shared seed, the same checkpoint, and a 512-token cap. The interfaces are direct, direct with callable forward/inverse definitions, forced forward coordinates and forced inverse coordinates. Require Lean acceptance and an axiom audit; certify transport of the two coordinate statements back to the original goal independently. Report sampled seeds and decoded outputs separately. A forced-coordinate success demonstrates composition with a supplied map. Choosing a map in the direct interface would be stronger evidence of autonomous use. No training, checkpoint search or held-out claim.

## Post-hoc sign intervention

The fresh coordinate results motivate a prediction before recompilation. Negating only the second literal witness should rescue inverse-coordinate attempts that chose the unreflected fundamental seed and can close the remaining goals. Flipping both coordinates should preserve eligibility and serve as a control for editing the witness. Keep the entire generated proof tail fixed. Also compile every distinct successful fresh coordinate proof as an explicit proof of the original theorem using the verified equivalence.

## Results

On 16 fresh matched draws per interface the direct theorem, callable menu, forward coordinates and inverse coordinates gave respectively 0, 0, 6 and 0 accepted proofs. All six forward successes used (5,2), which decodes to (49,20). They share one complete proof text. Lean accepted that text as a proof of the original theorem through forward_equiv. The inverse arm selected (5,2) ten times; it decodes there to the forbidden (1,0). On the other six inverse draws the seed (5,3) failed the norm condition.

Reflecting only y rescued all ten eligible inverse proof bodies (10/16), and destroyed all six forward successes (0/16). Negating both coordinates preserved the original outcome in each arm (6/16 and 0/16). This identifies a sign-sensitive preferred seed as the source of this observed asymmetry. On frozen unrestricted bodies the same forward scaffold closed 10/16 without changing even one token; the six remaining bodies used ring and left conjunction goals open. On the frozen second-round blocked bodies it closed 1/16. All direct and inverse replay cells were zero.

Job 1399141 ran for 4m14s. All 64 fresh samples and both sets of 16 historical samples were reconciled to their Lean sources and verdicts. The forward construction is supplied by the experiment. No independent model discovery of the recurrence or policy update is demonstrated here.
