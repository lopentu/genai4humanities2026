"""Generate v3 evidence, scopes and explicit provenance; no model outputs."""
from __future__ import annotations
import argparse, csv, hashlib, importlib.metadata, json, platform, subprocess
from datetime import datetime, timezone
from pathlib import Path
from minitok import MiniTok
import metrics as M
import stats as S
import stimuli as ST
import vocab_audit as VA
ENCODINGS=['cl100k_base','o200k_base']

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def run(ranks_dir,out,encodings=ENCODINGS):
    encs={n:MiniTok.from_ranks_file(ranks_dir/f'{n}.js',name=n) for n in encodings}
    design=ST.expand(); specs=ST.scope_specs(); rows={}; analysis={}
    for name,enc in encs.items():
        rows[name]=[{**cell,**M.text_metrics(enc,cell['text']), 'encoding':name} for cell in design]
        analysis[name]={}
        for key,scope in specs.items():
            rs=[r for r in rows[name] if r['item_id'] in scope['items'] and r['lexicon'] in scope['lexicons']]
            cats=sorted({r['category'] for r in rs})
            analysis[name][key]=dict(effects=S.decompose(rs,lexicons=scope['lexicons']),
              fragments=S.decompose(rs,key='n_utf8_fragments',lexicons=scope['lexicons']),
              by_category={c:S.decompose([r for r in rs if r['category']==c],lexicons=scope['lexicons']) for c in cats})
    constructions=[]
    for p in ST.CONSTRUCTION_PROBES:
        d=dict(p)
        for name,enc in encs.items():
            d[name]={k:M.token_details(enc,p[k]) for k in ('canonical','variant')}
        d['comparison_type']='identity reference' if p['canonical']==p['variant'] else 'surface illustration; not semantic minimal pair'
        constructions.append(d)
    root=Path(__file__).resolve().parent
    try: rev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,stderr=subprocess.DEVNULL).decode().strip()
    except Exception: rev='unversioned'
    payload=dict(meta=dict(version=3,generated=datetime.now(timezone.utc).isoformat(timespec='seconds'),
      source_base_commit=rev,python=platform.python_version(),n_items=len(ST.ITEMS),n_cells=len(design),encodings=encodings,
      bootstrap_seed=S.SEED,bootstrap_replicates=S.N_BOOT,bootstrap_estimand='mean item-level contrast; percentile interval',
      packages={n:importlib.metadata.version(n) for n in ['regex','opencc-python-reimplemented','jieba','numpy','scipy']},
      source_sha256={p.name:sha(p) for p in sorted(root.glob('*.py'))},
      rank_sha256={n:sha(ranks_dir/f'{n}.js') for n in encodings},rank_package='js-tiktoken@1.0.15',browser_bundle_sha256=sha(root/'assets/tokenizer/tokenizer.mjs'),
      validation_status='self-authored; author template screening; no native-speaker or downstream validation'),
      scopes=specs,items=[ST.item_metadata(i) for i in ST.ITEMS],design=design,rows=rows,analysis=analysis,
      constructions=constructions,vocab_audit={n:dict(coverage=VA.coverage_asymmetry(e),profile=VA.length_profile(e)) for n,e in encs.items()})
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=1,allow_nan=False),encoding='utf-8')
    with out.with_name('measurements.csv').open('w',encoding='utf-8',newline='') as f:
        fields=['encoding','item_id','category','script','lexicon','text','original_surface','n_tokens','n_han','n_codepoints','tokens_per_han','tokens_per_codepoint','n_utf8_fragments','han_split_rate','han_one_token_rate','fertility','boundary_f1']
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); writer.writeheader()
        for rs in rows.values(): writer.writerows(rs)
    for n in encodings:
        print(n)
        for k in specs: print(k,len(specs[k]['items']),S.fmt(analysis[n][k]['effects']['script_trad_minus_simp'],' tokens'))
    print('wrote',out)
    return payload

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--ranks',type=Path,default=Path('ranks')); ap.add_argument('--out',type=Path,default=Path('data/study.json'))
    a=ap.parse_args(); run(a.ranks,a.out)
