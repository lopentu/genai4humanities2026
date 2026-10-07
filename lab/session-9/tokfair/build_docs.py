"""Render Markdown docs with pinned Markdown, no external CSS dependency."""
from pathlib import Path
import markdown
import argparse

def render(source,out,title,back):
    body=markdown.markdown(source.read_text(encoding='utf-8'),extensions=['tables','fenced_code'])
    body=body.replace('<table>','<div class="scroll"><table>').replace('</table>','</table></div>')
    style=Path('web/docs.css.html').read_text(encoding='utf-8')
    out.write_text(f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>{style}</head><body><main class="wrap"><a href="{back}">← 返回課程／實驗</a>{body}</main></body></html>',encoding='utf-8')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--courses',action='store_true');a=p.parse_args()
    render(Path('index.md'),Path('index.html'),'Tokenization v3 · 程式與作業','../index.html#work' if a.courses else '../zh-tokenizer.html')
    render(Path('assignment1-tokenization-unfairness.md'),Path('assignment1.html'),'Tokenization v3 · 延伸練習','index.html')
