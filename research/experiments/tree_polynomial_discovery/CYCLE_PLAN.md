# Follow-up: the discovered zero-hit bottleneck and complete cycle search

Registered after observing the first panel at 170/186 completed runs:
zero successes at the assigned target in all 170, only one off-target
violation. Meanwhile the historical audit shows no verified successes in
99,980 valid fresh transformer generations, but 39,766 in the final
optimized elite set. This is evidence that reproducing the constructive
success may require the actual local optimizer rather than additional
seeds of our lighter search/PG policy. This followup tests a different
mechanism, not statistical redundancy.

Hypothesis: evaluating every deletion from the cycle created by a native
nonedge insertion provides access to useful objects missed by sampling
one deletion; iterative elite learning may supply better starting trees
than uniform generation, even if the policy alone yields zero successes.

Six tasks: original five plus historical n60/i30, where existing artifact
shows thousands of successes. Cross raw/normalized terminal scores,
cycle-complete vs random-single deletion, uniform vs learned CEM starts,
two paired seeds 42/43. 96 runs, 1,048,576 verifier calls each for
independence, 524,288 for slower domination, total 92,274,688.
At the first-hit call index assess whether discoveries occur below
the original 131,072-call pilot budget. Same per-task exact global
budget across all arms; overhead and search episodes counted separately.
Max ten accepted changes, max 500 candidate checks per start, 64
starts per CEM update, random nonedge ordering. Local search never
receives a known witness. All deletions on a selected cycle enumerated
unless whole cycle would exceed remaining cap; original score cached.
Single deletion draws one deletion from that same cycle, not previous
panel random-cut/reconnect. This is a paper-inspired comparator, not
byte-for-byte reproduction of their Julia local search (no path-to-star
reset, no special penalty, capped checks). CEM is elite imitation on
locally optimized outputs, not on-policy RLVR. Record separate
initial/final search successes and frozen generator-only evaluations.
If neither search nor learned starts gives positive experience, report
boundary and stop rather than keep increasing seeds. If hits arise,
inspect first hit and structural diversity before further intervention.

Registered after first-panel job 2956895 reached 170 successful
completions with no assigned-target hits; no need to wait for slow
remaining recombination arms to assess the already completed controls.
