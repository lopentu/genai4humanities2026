"""v3 within-item contrasts: mean/percentile-bootstrap CI is the primary
estimand. Wilcoxon is supplementary and tests a different signed-rank null.
Self-authored item resampling does not establish population representativeness.
"""
from __future__ import annotations
import hashlib
import numpy as np
from scipy import stats as sps
SEED=20261007
N_BOOT=10000

def paired_bootstrap(diffs,n_boot=N_BOOT,alpha=.05):
    d=np.asarray(diffs,dtype=float); d=d[np.isfinite(d)]
    if not len(d): return dict(mean=None,lo=None,hi=None,n=0)
    # Stable per-contrast RNG: adding a subset cannot change other intervals.
    digest=hashlib.sha256(d.astype('<f8').tobytes()).digest()
    rng=np.random.default_rng(SEED ^ int.from_bytes(digest[:4],'little'))
    means=d[rng.integers(0,len(d),size=(n_boot,len(d)))].mean(axis=1)
    return dict(mean=float(d.mean()),lo=float(np.quantile(means,alpha/2)),hi=float(np.quantile(means,1-alpha/2)),n=len(d))

def wilcoxon(diffs):
    d=np.asarray(diffs,dtype=float); d=d[np.isfinite(d)]; nz=d[d!=0]
    if len(nz)<3: return dict(p=None,rank_biserial=None,n_nonzero=len(nz))
    result=sps.wilcoxon(nz,alternative='two-sided',zero_method='wilcox',method='auto')
    ranks=sps.rankdata(abs(nz)); wp=ranks[nz>0].sum(); wm=ranks[nz<0].sum()
    return dict(p=float(result.pvalue),rank_biserial=float((wp-wm)/(wp+wm)),n_nonzero=len(nz))

def describe(diffs): return {**paired_bootstrap(diffs),**wilcoxon(diffs), 'diffs':[float(x) for x in diffs]}

def decompose(rows,key='n_tokens',lexicons=('tw','cn')):
    by={}
    for r in rows: by.setdefault(r['item_id'],{})[r['script'],r['lexicon']]=r[key]
    # Complete cases only; never average different sets of conditions.
    by={i:m for i,m in sorted(by.items()) if all((s,l) in m for s in ('trad','simp') for l in lexicons)}
    out={}
    out['script_trad_minus_simp']=describe([np.mean([m['trad',l]-m['simp',l] for l in lexicons]) for m in by.values()])
    for l in lexicons:
        if l=='cn': continue
        out[f'lexicon_{l}_minus_cn']=describe([np.mean([m[s,l]-m[s,'cn'] for s in ('trad','simp')]) for m in by.values()])
        out[f'interaction_{l}']=describe([(m['trad',l]-m['trad','cn'])-(m['simp',l]-m['simp','cn']) for m in by.values()])
        out[f'lexicon_{l}_at_simp']=describe([m['simp',l]-m['simp','cn'] for m in by.values()])
        out[f'script_at_{l}']=describe([m['trad',l]-m['simp',l] for m in by.values()])
        out[f'diagonal_{l}']=describe([m['trad',l]-m['simp','cn'] for m in by.values()])
        out[f'relative_{l}']=describe([(m['trad',l]/m['simp','cn']-1) for m in by.values() if m['simp','cn']])
    return out

def fmt(d,unit=''):
    return f"{d['mean']:+.3f}{unit} [{d['lo']:+.3f}, {d['hi']:+.3f}], n={d['n']}"
