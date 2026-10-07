"""v3 measurement definitions. UTF-8 fragments are observations, not causes.
Boundary agreement uses a common UTF-8 byte coordinate system. Jieba is a
reference segmenter, not human gold. No downstream competence is measured.
"""
from __future__ import annotations
import math
from collections import Counter
import regex as re
HAN=re.compile(r"\p{Script=Han}")
try:
    import jieba
    jieba.setLogLevel(60)
except ImportError:
    jieba=None

def n_han(text): return len(HAN.findall(text))

def token_details(enc,text):
    ids=enc.encode(text); raw=text.encode("utf-8"); pos=0; out=[]
    assert enc.decode_bytes(ids)==raw, "token bytes must reconstruct the input"
    for tid in ids:
        b=enc._inv[tid]
        try: surface=b.decode("utf-8"); valid=True
        except UnicodeDecodeError: surface=None; valid=False
        out.append(dict(id=tid,hex=b.hex(" "),byte_start=pos,byte_end=pos+len(b),surface=surface,valid_utf8=valid))
        pos+=len(b)
    return out

def token_spans(enc,text):
    """Actual token intervals in bytes, including boundaries inside characters."""
    return [(p['byte_start'],p['byte_end']) for p in token_details(enc,text)]

def word_spans(text):
    if jieba is None: raise RuntimeError("Install jieba for reference word boundaries")
    spans=[]; pos=0
    for w in jieba.cut(text,cut_all=False):
        n=len(w.encode('utf-8')); spans.append((pos,pos+n)); pos+=n
    return spans

def boundaries(spans): return {b for a,b in spans[:-1]}

def boundary_f1(pred,gold):
    if not pred and not gold: return 1.0
    tp=len(pred & gold); p=tp/len(pred) if pred else 0; r=tp/len(gold) if gold else 0
    return 2*p*r/(p+r) if p+r else 0.0

def text_metrics(enc,text,use_jieba=True):
    ps=token_details(enc,text); nt=len(ps); nh=n_han(text)
    spans={(p['byte_start'],p['byte_end']) for p in ps}; pos=0; exact=0; split=0
    ends={p['byte_end'] for p in ps}
    for c in text:
        stop=pos+len(c.encode('utf-8'))
        if HAN.fullmatch(c):
            exact+=int((pos,stop) in spans)
            split+=int(any(pos<b<stop for b in ends))
        pos=stop
    nf=sum(not p['valid_utf8'] for p in ps)
    out=dict(n_tokens=nt,n_han=nh,n_codepoints=len(text),n_bytes=len(text.encode('utf-8')),
        tokens_per_han=nt/nh if nh else None,tokens_per_codepoint=nt/len(text) if text else None,
        bytes_per_token=len(text.encode('utf-8'))/nt if nt else None,
        n_utf8_fragments=nf,utf8_fragment_rate=nf/nt if nt else 0,
        han_one_token_rate=exact/nh if nh else None,han_split_rate=split/nh if nh else None,
        token_details=ps)
    if use_jieba and jieba is not None:
        ws=word_spans(text); out.update(n_reference_units=len(ws),fertility=nt/len(ws) if ws else None,
          boundary_f1=boundary_f1(boundaries([(p['byte_start'],p['byte_end']) for p in ps]),boundaries(ws)))
    return out

def parity(a,b): return a/b if b else None

def premium(a,b): return a/b-1 if b else None

def empirical_renyi_uniformity(ids,alpha=2.5):
    """H_alpha / log(number of observed token types), a sample description.
    This is not a universal tokenizer quality score or a verified paper metric.
    """
    counts=Counter(ids); total=sum(counts.values())
    if len(counts)<2: return None
    h=math.log(sum((n/total)**alpha for n in counts.values()))/(1-alpha)
    return h/math.log(len(counts))
