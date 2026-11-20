import tempfile
from pathlib import Path
import unittest
import torch
from transformers import LlamaConfig, LlamaForCausalLM
from scripts.project import policy_update_math as m
from scripts.project import run_policy_improvement as run


class PolicyUpdateTests(unittest.TestCase):
    def test_reward_matching_and_incorrect_gating(self):
        rows=[dict(id=str(i),reward_eligible=True,local_accepted=i<4,
                   cross_reward=[0.,1.,1/3,2/3][i] if i<4 else 0.) for i in range(16)]
        traces={str(i):dict(response_token_ids=[1]*(i+1),sample_index=i) for i in range(16)}
        rewards=m.reward_vectors(rows,traces)
        self.assertEqual(sorted(rewards['length']),sorted(rewards['cross']))
        self.assertEqual(rewards['length'][:4],[1.,2/3,1/3,0.])
        self.assertEqual(rewards['length'][4:],[0.]*12)
        rows[5]['cross_reward']=1.
        with self.assertRaises(ValueError): m.reward_vectors(rows,traces)
        rows[5]['cross_reward']=0.
        rows[0]['reward_eligible']=False
        with self.assertRaises(ValueError): m.reward_vectors(rows,traces)

    def test_advantages_and_policy_gradient_sign(self):
        self.assertEqual(m.advantages([1.]*16),[0.]*16)
        self.assertAlmostEqual(sum(m.advantages([0.,1.,1.,0.])),0.)
        for advantage,sign in [(1.,-1.),(-1.,1.)]:
            logp=torch.tensor([-2.],requires_grad=True)
            loss,*_=m.loss_terms(logp,logp.detach(),logp.detach(),advantage,1.,'cross')
            loss.backward()
            self.assertEqual(float(logp.grad.sign()),sign)
        # Positive advantage beyond upper clipping boundary has no actor gradient.
        logp=torch.tensor([-1.],requires_grad=True)
        loss,*_=m.loss_terms(logp,torch.tensor([-2.]),logp.detach(),1.,1.,'cross',beta=0.)
        loss.backward()
        self.assertEqual(float(logp.grad),0.)

    def test_response_mask_and_adapter_roundtrip(self):
        torch.manual_seed(9)
        model=LlamaForCausalLM(LlamaConfig(vocab_size=64,hidden_size=32,intermediate_size=64,
            num_hidden_layers=1,num_attention_heads=4,num_key_value_heads=4)).eval()
        model.requires_grad_(False)
        prompt,response=[1,4,7],[8,9,2]
        actual=m.response_log_probs(model,prompt,response,'cpu')
        ids=torch.tensor([prompt+response])
        logits=model(ids).logits[0].float().log_softmax(-1)
        expected=torch.stack([logits[len(prompt)-1+i,t] for i,t in enumerate(response)])
        torch.testing.assert_close(actual,expected)
        frozen={k:v.clone() for k,v in model.state_dict().items()}
        model=run.add_adapter(model)
        opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=.01)
        loss,*_=m.loss_terms(m.response_log_probs(model,prompt,response,'cpu'),actual,actual,1.,1.,'replay')
        loss.backward(); opt.step()
        model.eval()
        changed=m.response_log_probs(model,prompt,response,'cpu').detach()
        self.assertGreater(float((changed-actual).abs().max()),0.)
        with model.disable_adapter():
            torch.testing.assert_close(m.response_log_probs(model,prompt,response,'cpu'),actual,rtol=0,atol=0)
        with tempfile.TemporaryDirectory() as d:
            model.save_pretrained(d,safe_serialization=True)
            base=LlamaForCausalLM(model.config)
            base.load_state_dict(frozen)
            base.requires_grad_(False)
            restored=run.add_adapter(base,Path(d)).eval()
            torch.testing.assert_close(m.response_log_probs(restored,prompt,response,'cpu'),changed,rtol=0,atol=0)


if __name__=='__main__': unittest.main()
