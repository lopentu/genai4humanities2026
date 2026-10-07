"""Independent official-tiktoken checks, byte reconstruction, controls, and statistics.
Run after run_study.py. Initial official rank download may require network.
"""
import json, hashlib, random
from pathlib import Path
import tiktoken
from minitok import MiniTok
import metrics as M
import stats as S
import stimuli as ST

def validate():
    d=json.loads(Path('data/study.json').read_text()); cases=[c['text'] for c in ST.expand()]
    cases+=['軟體','軟件','软件','𠮷野家','研究生命起源','中文🙂👩🏽‍💻English','�','<|endoftext|>','\n  a\t中文\r\n','', '1000 1,000 一千','café e\u0301', '</script>', '\ufeff中文', '中文\ufeff']
    rng=random.Random(20261007)
    alphabet='軟體軟件软件繁簡研究生命起源中文 ABC123，。🙂𠮷\n'
    cases+=[''.join(rng.choices(alphabet,k=rng.randint(1,80))) for _ in range(200)]
    checks=0
    for name in d['meta']['encodings']:
        mini=MiniTok.from_ranks_file(Path('ranks')/f'{name}.js',name=name); official=tiktoken.get_encoding(name)
        assert mini.ranks==official._mergeable_ranks
        for text in cases:
            ids=mini.encode(text); assert ids==official.encode_ordinary(text),(name,text)
            assert mini.decode_bytes(ids)==text.encode('utf-8')
            ps=M.token_details(mini,text)
            assert b''.join(bytes.fromhex(p['hex']) for p in ps)==text.encode('utf-8')
            checks+=1
        assert M.text_metrics(mini,'�')['n_utf8_fragments']==0
        for scope,spec in d['scopes'].items():
            a=d['analysis'][name][scope]['effects']
            for lex in spec['lexicons']:
                if lex=='cn': continue
                # Exact baseline path, not an additive claim about marginal effects.
                assert abs(a[f'diagonal_{lex}']['mean']-a[f'lexicon_{lex}_at_simp']['mean']-a[f'script_at_{lex}']['mean'])<1e-10
            assert a['script_trad_minus_simp']['n']==len(spec['items'])
        ctrl=d['analysis'][name]['controls']['effects']
        assert ctrl['lexicon_tw_minus_cn']['mean']==ctrl['lexicon_hk_minus_cn']['mean']==0
        for r in d['rows'][name]:
            for k,v in M.text_metrics(mini,r['text']).items(): assert r[k]==v,(name,r['item_id'],k)
    assert ST.expand([])==[]
    assert M.boundary_f1({1,2},{2,3})==.5
    assert S.paired_bootstrap([1,2,3])==S.paired_bootstrap([1,2,3])
    report=dict(status='passed',official_tiktoken=tiktoken.__version__,encoder_cases=checks,
       scopes={k:len(v['items']) for k,v in d['scopes'].items()},study_sha256=hashlib.sha256(Path('data/study.json').read_bytes()).hexdigest(),
       checks=['official rank and token-ID equivalence (ordinary text)','all measured rows recomputed','UTF-8 byte reconstruction','literal replacement character is not a fragment','complete-item scope counts','exact-control lexical differences zero','baseline decomposition identity','stable bootstrap seed'],
       limits=['No native-speaker validation','No downstream model evaluation','Browser/live deployment tested separately'])
    Path('data/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': validate()
