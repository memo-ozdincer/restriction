# Hanoi failure mechanism: policy capacity and gradient alignment

Registered before the full diagnostic (a preliminary LP probe already
found strict linear separability for 1..8 disks). The previously observed
shared-linear-policy failure might be representational incapacity, or
optimization under competing state distributions. Test whether the
unique optimal root route is expressible by the exact same affine-free
linear logits with legal-action masking. If feasible, pure lack of
expressivity cannot explain the root task failure.

A second offline diagnostic computes exact expected finite-horizon
policy gradients under root, uniform nonterminal starts and goal/root
random walks, and measures their alignment with the original root
log-success gradient. Analyze both the initialized and saved final
linear/tabular policies. No learner is updated; exact shortest path
and state distances are used only as independent probes. This is a
mechanism audit, not supervised training or a proposed curriculum.

## Results

The linear architecture can express the complete optimal root policy:
verified LP witnesses have minimum margin at least 1, and scaling their
weights by 30 gives root success probabilities 0.9999999999975 (five
disks) and 0.9999999999966 (six disks). These are offline oracle
certificates, not training inputs. This rules out insufficient capacity
to represent the root route, not insufficient capacity to represent all
routes simultaneously.

The table summarizes saved policies (means across existing seeds).
The log change is final minus initial natural-log root success.
Cosines compare the exact reset-objective gradient to the gradient of
log root success. For switched runs, the final cosine is a
counterfactual evaluation of the original reset objective.

| Disks | Policy | Reset | Initial cosine | Final cosine | Log root success change |
|---|---|---|---:|---:|---:|
| 5 | Linear | Uniform | .285 | .012 | -64.29 |
| 5 | Linear | Goal walk | .246 | -.195 | -21.54 |
| 5 | Linear | Uniform then root | .285 | -.163 | -45.32 |
| 5 | Tabular | Uniform | .265 | .205 | +32.82 |
| 5 | Tabular | Uniform then root | .265 | .003 | +33.66 |
| 6 | Linear | Uniform | .216 | .006 | -93.24 |
| 6 | Linear | Goal walk | .178 | -.138 | -24.44 |
| 6 | Tabular | Uniform | .208 | .152 | +50.83 |
| 6 | Tabular | Uniform then root | .208 | .175 | +42.81 |

Root-only controls show zero parameter change. Exact root probabilities
match saved results; directional finite differences agree with the
analytic gradient for all four reset distributions and both parameter
types (five disks, random weights, central step 1e-4, relative tolerance
1e-5 and absolute tolerance 1e-11).

The intervention unlocked reward, but under shared linear weights it
also dramatically reduced probability of the original solution. This
is stronger than a simple lack-of-reward explanation. Tabular policies
use the same initial action probabilities but have a different
parameter-sharing geometry. Six-disk tabular improvement still does not
yield a practically successful policy within the tested budget.

Endpoint gradients are not a causal reconstruction of the training
trajectory. The exact expected gradients also differ from sampled
optimizer updates. A useful next discriminating test is to log root
success, reward rate and alignment through training, then compare
parameter-sharing architectures under identical reset and reward
budgets. No shortest-path information should enter the learner.
