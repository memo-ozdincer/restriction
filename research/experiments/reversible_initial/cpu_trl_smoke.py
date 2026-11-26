"""CPU-only trainer wiring test; random tiny weights, never a research result."""
import argparse, tempfile, torch
from pathlib import Path
from collections import Counter
from transformers import AutoTokenizer, Qwen2Config, Qwen2ForCausalLM, set_seed
from peft import LoraConfig
from datasets import Dataset
from trl import GRPOTrainer
from train_grpo import make_config, training_rows, reward_records
set_seed(20261127)
torch.set_num_threads(2)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tokenizer',required=True)
model_path=parser.parse_args().tokenizer
tok=AutoTokenizer.from_pretrained(model_path, local_files_only=True)
tok.padding_side='left'
if tok.pad_token_id is None: tok.pad_token=tok.eos_token
model=Qwen2ForCausalLM(Qwen2Config(vocab_size=len(tok),hidden_size=16,intermediate_size=32,num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=2,max_position_embeddings=1024,bos_token_id=tok.bos_token_id,eos_token_id=tok.eos_token_id,pad_token_id=tok.pad_token_id))
rows=training_rows('exploratory',2)
seen=[]
def reward(completions,circuit_json,trainer_state,completion_ids,**kwargs):
    results=reward_records(completions,circuit_json)
    assert len(results)==2 and len({r['group_id'] for r in results})==1
    assert len(completion_ids)==2
    seen.append(results[0]['group_id'])
    # The strict circuit reward is separately unit-tested; inject a mixed group here
    # solely to test that the trainer's policy update actually changes weights.
    return [1,0]
with tempfile.TemporaryDirectory() as tmp:
    cfg=make_config(Path(tmp),2,2,4,20261127,cpu=True)
    cfg.save_strategy='no'
    cfg.generation_kwargs={'forced_eos_token_id':tok.eos_token_id}
    trainer=GRPOTrainer(model=model,args=cfg,processing_class=tok,reward_funcs=reward,train_dataset=Dataset.from_list(rows),peft_config=LoraConfig(r=2,lora_alpha=4,target_modules='all-linear',task_type='CAUSAL_LM'))
    initial={n:p.detach().clone() for n,p in trainer.model.named_parameters() if p.requires_grad}
    trainer.train()
    assert any(not torch.equal(initial[n],p) for n,p in trainer.model.named_parameters() if p.requires_grad), 'Mixed-reward smoke did not update the adapter'
    assert trainer.state.global_step==2 and Counter(seen)=={0:1,1:1}, (trainer.state.global_step,seen)
print('CPU TRL integration: two optimizer steps, two independent rollout groups, four proposals verified, adapter changed under synthetic mixed rewards.')
