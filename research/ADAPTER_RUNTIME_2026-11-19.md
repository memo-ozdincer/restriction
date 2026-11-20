# Isolated adapter runtime for the upcoming training comparison

The pinned inference runtime has Transformers 4.40.1 and PyTorch 2.3.0+cu121,
but its installed PEFT 0.19.1 fails to import `EncoderDecoderCache`. The pinned
interpreter also has no pip module. No shared package was upgraded or replaced.

Downloaded `peft-0.10.0-py3-none-any.whl` directly from the PyPI version metadata,
verified its SHA-256, and extracted it into a new isolated overlay:

```
../environment/overlays/peft-0.10.0
```

Wheel SHA-256:
`d5249c97e818d3e31f92553c73c2953acd0ec12649b8b749afff7152cbc86cbb`.
The exact URL and local path are in
`experiments/adapter_runtime_20261119/setup-receipt.json`. The wheel is also in
the raw cross-context-credit archive so migration need not depend on PyPI.
Its [official tagged requirements](https://github.com/huggingface/peft/blob/v0.10.0/setup.py)
are compatible at the metadata level; the actual runtime check below is the
stronger local evidence. This is not a recommendation to downgrade other projects.

Opt in for a command with `PYTHONPATH` pointing to that overlay, leaving the
ordinary inference environment untouched. For the CPU engineering check:

```bash
PYTHONPATH="$PWD/../environment/overlays/peft-0.10.0" \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
../environment/venv/bin/python scripts/project/check_adapter_runtime.py \
  --output ../runs/adapter-runtime-check-NEW
```

The actual check used a tiny randomly initialized one-layer Llama on CPU,
256 trainable LoRA parameters, and one synthetic optimizer step. It loaded no
research checkpoint. The adapter changed logits while the disabled-adapter
reference remained bitwise unchanged. Save/reload reproduced logits exactly;
merge differed by at most 8.95e-8. The recorded PEFT warning concerns the
synthetic base model's absent repository config, not a failed reload.

These checks establish basic API/update/persistence compatibility only. They
do not establish 7B GPU memory feasibility, validate the future RL loss, or
count as scientific training. Exact-token collection, loss/gradient checks,
full-size GPU execution, and the matched training/evaluation protocol remain
to be completed before a research result can be claimed.
