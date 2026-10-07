"""Embed v3 data safely in the static template. Live measurements use a local bundle."""
import argparse, json
from pathlib import Path

def build(study,template,out,site="genai"):
    data=json.loads(study.read_text(encoding='utf-8'))
    assert data['meta']['version']==3
    # Retain all byte evidence and item contrasts; no lossy U+FFFD heuristics.
    compact=json.dumps(data,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    html=template.read_text(encoding='utf-8')
    if html.count('__STUDY_DATA__')!=1: raise ValueError('Expected one data placeholder')
    if site=='courses':
        html=html.replace('href="tokfair/"','href="index.html"').replace('href="tokfair/','href="').replace("import('./tokfair/","import('./")
        html=html.replace('href="zh-tokenizer-v2.html"','href="https://lopentu.github.io/genai4humanities2026/lab/session-9/zh-tokenizer-v2.html"')
        html=html.replace('href="zh-tokenizer-v1.html"','href="https://lopentu.github.io/genai4humanities2026/lab/session-9/zh-tokenizer-v1.html"')
        html=html.replace('href="../../practice/lab/session-9/"','href="../index.html#work"').replace('返回 Session 9','返回 LING5006 作業')
        html=html.replace('cd lab/session-9/tokfair','cd cllt2026/a1').replace('--out ../zh-tokenizer.html','--out zh-tokenizer.html --site courses')
        html=html.replace('GenAI for Humanities · Session 9 /','LING5006 · A1 參考 /')
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(html.replace('__STUDY_DATA__',compact),encoding='utf-8')
    print('wrote',out)
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--study',type=Path,default=Path('data/study.json')); ap.add_argument('--template',type=Path,default=Path('web/zh-tokenizer.template.html')); ap.add_argument('--out',type=Path,default=Path('../zh-tokenizer.html')); ap.add_argument('--site',choices=['genai','courses'],default='genai')
    a=ap.parse_args(); build(a.study,a.template,a.out,a.site)
