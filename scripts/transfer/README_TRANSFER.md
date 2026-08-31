# Restriction-RL portable bundle

This one top-level directory contains the repository and Git history, datasets,
exact base/C1/C3 model weights, run records and proof logs, the built DeepSeek
Lean verifier workspace, Lean 4.9.0-rc1, managed CPython 3.11.4, and the exact
installed Python/CUDA package environment.

## Use on the destination cluster

From the transferred directory:

```bash
source ./activate.sh
python ./verify_bundle.py "$RESTRICTION_BUNDLE_ROOT" --full-checksums
python ./verify_bundle.py "$RESTRICTION_BUNDLE_ROOT" --verify-manifest
scripts/project/preflight.sh
```

The second verification command reads every bundled byte and can take several
minutes. Run it after transfer and before submitting GPU work.

The Python environment contains CPython 3.11.4, PyTorch 2.3.0, CUDA runtime
12.1, cuDNN 8.9.2.26, NCCL 2.19.3, transformers 4.40.1, and vLLM 0.4.2. The
complete package inventory is `environment/requirements.installed.txt`.
Packages do not need to be resolved or downloaded on the destination.

The destination needs Linux x86-64, a compatible glibc, a sufficiently recent
NVIDIA driver for CUDA 12.1, and scheduler directives adapted to its account
and partition names. No model, dataset, Python package, Lean toolchain, mathlib,
or verifier download is required.

Activation sets these canonical paths:

- `$RESTRICTION_PROJECT_ROOT`
- `$RESTRICTION_BASE_MODEL_PATH`
- `$RESTRICTION_C1_MODEL_PATH`
- `$RESTRICTION_C3_MODEL_PATH`
- `$DEEPSEEK_PROVER_ROOT`
- `$ELAN_HOME`

## Transfer

For a resumable cluster-to-cluster copy that preserves local hardlink
deduplication:

```bash
rsync -aH --partial --info=progress2 restriction-rl-portable-20260831/ HOST:/DESTINATION/restriction-rl-portable-20260831/
```

`MANIFEST.sha256` uses paths relative to this top-level directory, so the
directory may be moved or renamed without invalidating the manifest.
