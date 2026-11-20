#!/usr/bin/env python3
"""CPU engineering check on a tiny random model; no research checkpoint read."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    import peft
    import torch
    import transformers
    from peft import LoraConfig, PeftModel, get_peft_model
    from transformers import LlamaConfig, LlamaForCausalLM
    torch.set_num_threads(1)
    config = LlamaConfig(vocab_size=64, hidden_size=32, intermediate_size=64,
        num_hidden_layers=1, num_attention_heads=4, num_key_value_heads=4,
        max_position_embeddings=64, attention_dropout=0.)
    torch.manual_seed(42)
    base = LlamaForCausalLM(config).eval()
    tokens = torch.tensor([[1, 7, 3, 11, 9, 2]])
    with torch.no_grad(): original = base(tokens).logits.clone()
    model = get_peft_model(base, LoraConfig(r=2, lora_alpha=4, lora_dropout=0.,
        target_modules=['q_proj', 'v_proj'], task_type='CAUSAL_LM')).eval()
    trainable = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
    assert trainable and all('lora_' in n for n, _ in trainable)
    optimizer = torch.optim.AdamW([p for _, p in trainable], lr=1e-3, weight_decay=0.)
    loss = model(tokens, labels=tokens).loss
    loss.backward()
    optimizer.step()
    optimizer.zero_grad(set_to_none=True)
    with torch.no_grad(): changed = model(tokens).logits.clone()
    with model.disable_adapter(), torch.no_grad(): reference = model(tokens).logits.clone()
    assert torch.equal(original, reference), 'Frozen reference changed'
    assert not torch.equal(original, changed), 'No demonstrated adapter update'
    model.save_pretrained(a.output / 'synthetic-adapter')
    torch.manual_seed(42)
    reloaded = PeftModel.from_pretrained(LlamaForCausalLM(config), a.output / 'synthetic-adapter').eval()
    with torch.no_grad(): restored = reloaded(tokens).logits
    assert torch.allclose(changed, restored, atol=1e-6, rtol=1e-6), 'Adapter reload changed output'
    merged = model.merge_and_unload().eval()
    with torch.no_grad(): merged_logits = merged(tokens).logits
    assert torch.allclose(changed, merged_logits, atol=1e-6, rtol=1e-6), 'Merge changed output'
    result = {'scope': 'CPU engineering check on randomly initialized tiny Llama; not scientific model training',
        'research_checkpoint_loaded': False, 'device': 'cpu', 'passed': True,
        'peft': peft.__version__, 'peft_module': peft.__file__, 'transformers': transformers.__version__,
        'torch': torch.__version__, 'synthetic_optimizer_steps': 1,
        'trainable_parameters': sum(p.numel() for _, p in trainable),
        'initial_loss': loss.item(), 'reference_unchanged': torch.equal(original, reference),
        'adapter_output_change': (changed-original).abs().max().item(),
        'reload_max_difference': (restored-changed).abs().max().item(),
        'merge_max_difference': (merged_logits-changed).abs().max().item(),
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (a.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
