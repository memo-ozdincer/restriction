"""Pure Python tests for retrospective proof tracking semantics."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/project'))
from track_near_misses import Bank, analyze, category, lines


def row(body, good=False, i='id', failure='lean_rejected'):
    return dict(proof=body,correct=good,proposal_id=i,failure_class=failure)


class NearMissTrackingTests(unittest.TestCase):
    def test_edit_positions_and_all_siblings(self):
        bank=Bank([row('a\nx\nb\n'),row('a\ny\nb\n',True),row('a\nb\n',True),
                   row('a\nx\nz\nb\n',True),row('x\na\nb\n',True)])
        s=bank.siblings(lines('a\nx\nb\n'))
        self.assertEqual({''.join(a) for a,*_ in s},{'a\ny\nb\n','a\nb\n','a\nx\nz\nb\n'})
        self.assertEqual({category(old,new) for a,i,sc,old,new in s},
                         {'missing_line','extra_line','different_tactic_head'})

    def test_observation_categories(self):
        k=('t','s','c')
        base=[row('a\nx\nb\n'),row('a\ny\nb\n',True)]
        data={'c0':{k:base},'c1':{k:[row('a\nz\nb\n',True),row('a\nw\nb\n')]},
              'c2':{k:[row('a\ny\nb\n',True),row('a\nx\nb\n',failure='timeout')]}}
        rec=analyze(data)['records'][0]
        self.assertEqual(rec['outcomes']['c1']['exact'],'unobserved')
        self.assertEqual(rec['outcomes']['c1']['family'],'both')
        self.assertEqual(rec['outcomes']['c2']['exact'],'corrected_only')
        self.assertEqual(rec['outcomes']['c2']['unresolved_ids'],['id'])

    def test_contradictory_and_short(self):
        k=('t','s','c')
        data={'c0':{k:[row('x\n'),row('x\n',True),row('y\n')]},
              'c1':{k:[row('x\n',True)]}}
        rec=analyze(data)['records']
        self.assertEqual(len(rec),1)
        self.assertNotIn('family',rec[0]['outcomes']['c1'])


if __name__=='__main__':
    unittest.main()
