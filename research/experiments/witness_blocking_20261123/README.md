# Blocking the empty witness

Hypothesis before replay: the eight-theorem pilot retained many spellings of the same empty witness, so excluding that witness will exhaust observed positive examples on theorem 11649. Replay every distinct parseable candidate from this theorem in every phase against a stronger goal requiring both sets to be nonempty. Separately test an explicit construction with Lean. The registered statement makes no requirement that the witnesses lie inside S.

## Recorded model proofs

Among 128 archived proposals for this training problem, Lean accepted 116 under the original statement. All 29 distinct accepted source bodies explicitly choose two empty sets. Replaying the 36 distinct proposed bodies under the nonempty condition yielded zero successes. A separately authored nonempty construction passed the same verifier and axiom audit. Rejecting the empty witness would remove every observed positive example on this problem.

## Two different mathematical targets

The released Lean statement quantifies over positive m and omits the containment of X and Y in S. For that formalization we checked an infinite family. Set n = 51m+1 and translate the triples {0,k+4,2k+5} and {1,k+2,2k+6} by n for any natural k. They are disjoint, avoid A, and match in both sums and squared sums. A separate Lean proof shows two-element sets with matching first and second moments must coincide. The construction and counting argument here were authored during analysis, independently of the sampled proofs.

The workbook's informal text in data/mff-lwb-10k-seen.parquet row with extra_info.index 1525 fixes m=42 and explicitly requires X,Y inside S. Its text permits empty sets as well. For the stronger nonempty reading, write B=S∖A. Its 42 elements lie between 1 and 2142. Assign each subset U the pair

    (sum of x, sum of x*(2142-x)) for x in U.

The first coordinate ranges from 0 to 42·2142. Each summand in the second coordinate is at most 1071². This gives at most 4,334,128,919,695 keys for 4,398,046,511,104 subsets. Two distinct subsets share a key. Their sums agree, and subtracting the second coordinate from 2142 times the first gives their equal sum of squares. Cancel the common elements. The differences are disjoint, and positivity forces both differences to be nonempty.

The executable search uses the equivalent collision statistic x·(2143−x)/2, which is always integral and saves a factor of about two in the key bound. All four deterministic example complements produced nonempty witnesses. In the seeded example the disjoint sets {303,964,1717,1912} and {454,762,1657,2023} have matching first and second moments. The search returned after 90,200 subsets. That observed cost concerns this input only.

The pinned Lean runtime independently accepted both the finite pigeonhole theorem and its corollary for every allowed A of size 2100, with containment, disjointness, nonemptiness and both moment equalities. The axiom audit is in workbook-verdict.json. This is a reference proof for a future model experiment. The frozen prover has not been given this proof or evaluated on a new sample under the stronger statement.
