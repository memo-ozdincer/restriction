# Instrument history

These files preserve operational sources and a witness-only erratum from
October 26. They are provenance snapshots, not the current launch interface.
The diagnostic snapshots contain the original absolute paths and should not
be invoked as general-purpose tools. Use the current scripts under
`scripts/project/` with new output directories.

The initial production-check snapshot has SHA-256
`12fb04aaa95cdc228068791dc5fbd8f241cd81b8942b9c3cdca1d291dc617766`,
matching the source recorded by its failed run. It was reconstructed after
adding erratum support to the live script, then checked byte-for-byte by this
digest before publication. Later runs also save their actual runner source.

The witness erratum changes only three ambiguous names per rational proof.
Original frozen test tasks, model inputs, and witnesses remain available at
their unchanged hashes. Full evidence and costs are recorded in
`../../results/procedure_transfer_production_check_20261026.json`.
