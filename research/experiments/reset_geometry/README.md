# Reset geometry diagnostic

Registered hypothesis, before calculation: goal-centered resets in the
three-bit reversible environment mainly improve the initial probability
of terminal reward by reducing the shortest remaining distance. A
perturbation around the original hard start may retain a larger fraction
of the original task's difficulty, while same-distance resets can vary
state without reducing the minimum action count. Exact random-policy
success probabilities can distinguish these changes without training or
noise from model inference. This is a diagnostic, not evidence about
learned transfer. Use the existing exact-eight-gate root/target and
eight-action budget, identical transition and terminal semantics.

Additional diagnostic hypothesis: increasing only allowed action budget
may unlock initial rewards from the *same* root, avoiding reset-induced
distribution change. Compute exact random policy hitting probabilities
at horizons 8,12,16,24,32,64. This changes the training success criterion's
resource constraint; ordinary evaluation still uses 8. No learning run.

Results: root 1.4466e-6; root walk 1.222e-5; uniform 1.8249e-4;
goal walk 0.03651645; equal distance shell 8.8e-7; balanced shell
0.01445371. Goal walk yields roughly 25,000x the root hit probability.
Horizon slack at 24 actions gives 0.0002060 random-policy root probability.
All are hitting probabilities, computed by absorbing the goal in the
finite-horizon transition recurrence. Exact graph BFS supplies distance
statistics, not reward. Reproduce with python3 analyze.py.
