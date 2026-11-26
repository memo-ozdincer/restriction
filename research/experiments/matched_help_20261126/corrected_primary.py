"""One-factor corrective rerun of primary spontaneous-help protocol."""
import run
run.ROOT=run.ROOT/'corrected-primary'
run.ROOT.mkdir(exist_ok=True)
assert 'or other agents' in run.COMMON
run.COMMON=run.COMMON.replace(', or other agents','')
assert 'other agents' not in run.COMMON
run.main()
