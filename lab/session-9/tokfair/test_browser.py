"""Browser integration checks. Start a local HTTP server, then pass the
experiment URL. Needs requirements-browser.txt and Chrome or Playwright Chromium.
Output/snapshots use a temporary directory, not the source tree.
"""
import json,sys,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8000/zh-tokenizer.html'
import tempfile
output=Path(tempfile.mkdtemp(prefix='tokfair-v3-browser-'))
report={'url':base,'checks':[]}; errors=[]
with sync_playwright() as p:
 chrome=Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
 browser=p.chromium.launch(**({'executable_path':str(chrome)} if chrome.exists() else {}),headless=True)
 page=browser.new_page(viewport={'width':1280,'height':900},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(base,wait_until='domcontentloaded');page.wait_for_selector('#cellgrid .cell')
 assert page.locator('#cellgrid .cell').count()==4
 assert '29' in page.locator('#headline').inner_text()
 count=0
 scopes=page.evaluate('Object.keys(tokfair.DATA.scopes)')
 for scope in scopes:
  page.select_option('#sel-scope',scope)
  for enc in ['cl100k_base','o200k_base']:
   page.select_option('#sel-enc',enc)
   cats=page.locator('#sel-cat option').evaluate_all('(os)=>os.map(o=>o.value)')
   for cat in cats:
    page.select_option('#sel-cat',cat)
    assert page.locator('#cellgrid .cell').count()==(6 if scope.startswith('hk') or scope=='controls' else 4)
    assert page.locator('#effectbars svg').count() in [3,5]
    assert 'undefined' not in page.locator('main').inner_text()
    count+=1
 report['checks'].append({'scope_encoder_category_combinations':count})
 # A negative CI endpoint must be drawn left of the zero reference.
 page.select_option('#sel-scope','twcn_all');page.select_option('#sel-cat','all');page.select_option('#sel-enc','cl100k_base')
 assert page.evaluate("[...document.querySelectorAll('#effectbars svg')].some(s=>Number(s.querySelectorAll('line')[1].getAttribute('x1'))<250)")
 report['checks'].append('negative interval endpoints retain signed coordinates')
 # Exact controls yield lexical zero; costs validate invalid/zero settings.
 page.select_option('#sel-scope','controls');assert '逐字相同' in page.locator('#scope-note').inner_text()
 page.fill('#price','0');assert page.locator('#tbl-cost tbody tr').count()==12
 page.fill('#reserved','128000');assert page.locator('#tbl-cost tbody tr').count()==0
 page.fill('#reserved','8192');page.fill('#price','1');page.select_option('#denom','n_han')
 report['checks'].append('control scope and hypothetical cost edge cases')
 page.select_option('#sel-scope','twcn_screened');page.select_option('#sel-cat','all')
 with page.expect_download() as dl:page.click('#export-csv')
 dl.value.save_as(str(output/'export.csv'))
 import csv
 exported=list(csv.DictReader(Path(str(output/'export.csv')).open(encoding='utf-8-sig')));assert len(exported)==116
 with page.expect_download() as dl:page.click('#export-json')
 dl.value.save_as(str(output/'export.json'));assert json.loads(Path(str(output/'export.json')).read_text())['meta']['version']==3
 report['checks'].append('CSV 116 selected cells and complete JSON downloads')
 page.click('#load-tokenizer');page.wait_for_function('tokfair.live !== null',timeout=30000)
 # Compare actual browser bundle output to all precomputed token evidence.
 result=page.evaluate('''()=>{let n=0;for(const [enc,rows] of Object.entries(tokfair.DATA.rows)){for(const r of rows){const got=tokfair.live.measure(r.text,enc);if(JSON.stringify(got)!==JSON.stringify(r.token_details)){
 if(got.length!==r.token_details.length||got.some((p,i)=>Object.keys(p).some(k=>p[k]!==r.token_details[i][k])))throw Error(enc+' '+r.item_id);
 }n++;}}return n;}''')
 assert result==444;report['checks'].append({'browser_vs_python_token_evidence_cells':result})
 for text in ['�','<|endoftext|>','中文🙂👩🏽‍💻English','𠮷野家','</script>', '\ufeff中文', '中文\ufeff']:
  page.fill('#ta-a',text);page.wait_for_timeout(350);assert page.locator('#custom-out .warn').count()==0
 page.fill('#ta-a','');page.fill('#ta-b','');page.wait_for_timeout(350);assert '兩欄' in page.locator('#custom-out').inner_text()
 report['checks'].append('live Unicode, literal replacement/special strings, HTML text and empty inputs')
 page.select_option('#sel-scope','twcn_screened');page.fill('#ta-a','這個軟體最近更新了介面設計。');page.fill('#ta-b','这个软件最近更新了界面设计。')
 # Local-browser network disconnect keeps the embedded dataset usable.
 page.context.set_offline(True);page.select_option('#sel-enc','o200k_base');assert page.locator('#cellgrid .cell').count()==4
 page.context.set_offline(False)
 report['checks'].append('embedded analyses remain interactive without network')
 page.screenshot(path=str(output/'desktop.png'),full_page=False)
 for width in [390,768]:
  page.set_viewport_size({'width':width,'height':844})
  for scope in ['twcn_screened','hk_all']:
   page.select_option('#sel-scope',scope)
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),(width,scope)
 page.screenshot(path=str(output/'mobile.png'),full_page=False)
 report['checks'].append('390px and 768px viewport; 2x2 and 2x3 no page overflow')
 # Failed lazy bundle load can retry while analysis is still usable.
 context=browser.new_context();q=context.new_page();q.route('**/assets/tokenizer/tokenizer.mjs',lambda r:r.abort())
 q.goto(base,wait_until='domcontentloaded');q.click('#load-tokenizer');q.wait_for_function("document.querySelector('#load-tokenizer').textContent==='重試載入'")
 assert q.locator('#cellgrid .cell').count()==4
 context.close();report['checks'].append('lazy tokenizer failure leaves analyses available and offers retry')
 # Course and canonical documentation links are separately checked by HTTP audit.
 browser.close()
assert not errors,errors
report['browser_errors']=errors;report['status']='passed'
Path(str(output/'browser-report.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))

print("artifacts",output)
