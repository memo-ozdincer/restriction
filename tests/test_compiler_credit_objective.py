import sys
from pathlib import Path
import unittest
import torch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/project'))
from compiler_credit_objective import loss_terms


class CompilerCreditObjectiveTests(unittest.TestCase):
    def test_initial_gradient_only_selected_tokens(self):
        x=torch.tensor([-2.,-3.,-4.,-5.],requires_grad=True)
        loss,_,anchor=loss_terms(x,x.detach().clone(),torch.tensor([1.,0.,1.,0.]))
        loss.backward()
        self.assertEqual(anchor.item(),0.)
        self.assertTrue(torch.equal(x.grad,torch.tensor([-.5,0.,-.5,0.])))

    def test_reference_anchor_reaches_unselected_tokens(self):
        x=torch.tensor([-2.,-3.],requires_grad=True)
        loss,_,_=loss_terms(x,torch.tensor([-2.,-4.]),torch.tensor([1.,0.]),beta=.02)
        loss.backward()
        self.assertTrue(torch.allclose(x.grad,torch.tensor([-1.,.02])))

    def test_full_likelihood_and_invalid_masks(self):
        x=torch.tensor([-2.,-4.])
        loss,nll,anchor=loss_terms(x,x,torch.ones_like(x))
        self.assertEqual(loss.item(),3.)
        self.assertEqual(nll.item(),3.)
        self.assertEqual(anchor.item(),0.)
        for mask in [torch.zeros_like(x),torch.tensor([1.,.5])]:
            with self.assertRaises(ValueError):loss_terms(x,x,mask)


if __name__=='__main__':unittest.main()
