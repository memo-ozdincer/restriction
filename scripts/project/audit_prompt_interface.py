"""Authenticate C1's prompt format against saved native training tensors."""
import argparse
import json
import statistics
from pathlib import Path
import subprocess
from verl.protocol import DataProto
from transformers import AutoTokenizer
import interface_discovery_pilot as lean
from proof_prompt_interface import prompt,BOS,MODES


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('out',type=Path);a=p.parse_args();b=a.bundle;a.out.mkdir(parents=True,exist_ok=False)
    src=b/'runs/c1-grpo-default-full-20260814-seed42-5ced4c3/artifacts/train_batch_buffer/global_step_604'
    x=DataProto.load_from_disk(str(src));tok=AutoTokenizer.from_pretrained(str(b/'models/c1-final'),local_files_only=True)
    rows=x.batch['prompts'];mask=x.batch['attention_mask'][:,:rows.shape[1]];checks=[]
    for i in range(len(rows)):
        ids=rows[i][mask[i].bool()].tolist();statement=x.non_tensor_batch['theorem_statement'][i];informal=x.non_tensor_batch['informal_statement'][i]
        expected=tok.encode(prompt(statement,'native',informal),add_special_tokens=False)[-rows.shape[1]:]
        checks.append(dict(index=i,tokens=len(ids),first_id=ids[0],last_id=ids[-1],matches_native=ids==expected,ids_sha256=lean.sha(json.dumps(ids))))
    lean.write(a.out/'training-prompt-checks.json',checks)
    assert len(checks)==128 and all(c['matches_native'] and c['last_id']==tok.bos_token_id for c in checks)
    recent=b/'runs/contract-closure-20261124-1400174/experiment/transport';train=json.loads((recent.parent/'train.json').read_text())['transport'];records=json.loads((recent/'tokens.json').read_text());logs=json.loads((recent/'reload-probes.json').read_text());recent_checks=[]
    for t,r,lp in zip(train,records,logs):
        plain=lean.PREFIX+lean.HEADER+t['statement'];legacy=tok.encode(plain);native=tok.encode(prompt(t['statement'],'native'),add_special_tokens=False)
        joint=tok.encode(plain+t['response']);assert r['prompt_token_ids']==legacy and joint==legacy+r['response_token_ids']
        assert legacy==tok.encode(prompt(t['statement'],'legacy'),add_special_tokens=False)
        recent_checks.append(dict(id=t['id'],response_tokens=len(lp),tokenization_train_inference_consistent=True,
            legacy_first_id=legacy[0],legacy_last_id=legacy[-1],native_first_id=native[0],native_last_id=native[-1],
            legacy_equals_native=legacy==native,mean_response_nll=-statistics.mean(lp),first_six_response_nll=-sum(lp[:6])))
    lean.write(a.out/'recent-training-checks.json',recent_checks)
    historical=subprocess.check_output(['git','show','5ced4c3:verl/lean/prompts.py'],cwd=b/'repository',text=True)
    (a.out/'historical-prompts.py').write_text(historical)
    result=dict(passed=True,native_training_rows=128,exact_native_matches=sum(c['matches_native'] for c in checks),
        final_bos_rows=sum(c['last_id']==tok.bos_token_id for c in checks),leading_bos_rows=sum(c['first_id']==tok.bos_token_id for c in checks),
        recent_records=len(recent_checks),recent_legacy_native_matches=sum(c['legacy_equals_native'] for c in recent_checks),
        recent_train_inference_tokenization_consistent=all(c['tokenization_train_inference_consistent'] for c in recent_checks),
        bos_token=BOS,bos_id=tok.bos_token_id,training_buffer_sha256=lean.sha(src.read_bytes()),
        historical_prompt_source_sha256=lean.sha(historical),recent_tokens_sha256=lean.sha((recent/'tokens.json').read_bytes()),
        conclusion='Confirmed pretrained-interface mismatch; effect on correctness not yet measured. Recent standalone adapters are internally tokenization-consistent.')
    lean.write(a.out/'audit.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
