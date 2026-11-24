"""Explicit proof-prompt token boundaries; historical formats remain reproducible."""
from verl.lean.prompts import prompt_fn_deepseek
import interface_discovery_pilot as lean

MODES={'neither':(False,False),'legacy':(True,False),'native':(False,True),'both':(True,True)}
BOS='<｜begin▁of▁sentence｜>'


def prompt(statement,mode,informal=''):
    leading,trailing=MODES[mode]
    native=prompt_fn_deepseek(statement,informal,None,None)
    assert native==lean.PREFIX+lean.HEADER+informal+statement+BOS
    plain=native[:-len(BOS)]
    return (BOS if leading else '')+plain+(BOS if trailing else '')


class ExplicitTokenizer:
    """Disable implicit BOS insertion; all markers are explicit in prompt text."""
    def __init__(self,tokenizer):self.tokenizer=tokenizer
    def encode(self,text,**kwargs):
        kwargs.setdefault('add_special_tokens',False)
        return self.tokenizer.encode(text,**kwargs)
    def __getattr__(self,name):return getattr(self.tokenizer,name)
