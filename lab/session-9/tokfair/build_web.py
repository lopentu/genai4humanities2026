"""build_web.py — compile study.json + the page template into one static file.

    python build_web.py --study data/study.json \
                        --template web/zh-tokenizer.template.html \
                        --out ../lab/session-9/zh-tokenizer.html

The output is fully self-contained: every number on the page is baked in from
the study run, so the page renders identically offline and cannot drift from
the analysis.  The only network call is a lazy import of js-tiktoken, used
solely for the "type your own sentence" panel; if it fails the rest of the page
still works.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

KEEP_ROW = ("item_id", "category", "script", "lexicon", "n_tokens", "n_han",
            "n_byte_fallback", "byte_fallback_rate", "tokens_per_char",
            "char_integrity", "fertility", "boundary_f1", "attested", "pieces")

KEEP_STAT = ("mean", "lo", "hi", "p", "rank_biserial", "n")


def jsonable(obj):
    """NaN/Inf are legal in Python json.dumps but illegal in JSON.parse."""
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, dict):
        return {k: jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [jsonable(v) for v in obj]
    return obj


def trim_stat(d: dict) -> dict:
    return {k: d[k] for k in KEEP_STAT if k in d}


def _sanitize_pieces(pieces):
    """U+FFFD marks a byte-fragment token; carry that as JSON null instead.

    Embedding raw replacement characters in the page confuses downstream
    tooling (and some publishers reject them outright), and `null` states the
    intent more clearly than a character that merely failed to decode.
    """
    return [None if (p is None or "\ufffd" in p) else p for p in pieces]


def trim(payload: dict) -> dict:
    out = dict(meta=payload["meta"], hypotheses=payload["hypotheses"])
    out["items"] = [{k: it[k] for k in ("id", "category", "tw", "cn", "hk",
                                        "gloss", "probe", "hk_confidence")}
                    for it in payload["items"]]
    out["design"] = [{k: c[k] for k in ("item_id", "script", "lexicon", "text", "attested")}
                     for c in payload["design"]]
    out["rows"] = {}
    for enc, rows in payload["rows"].items():
        trimmed = []
        for r in rows:
            d = {k: r[k] for k in KEEP_ROW if k in r}
            if "pieces" in d:
                d["pieces"] = _sanitize_pieces(d["pieces"])
            trimmed.append(d)
        out["rows"][enc] = trimmed

    def trim_decomp(d):
        return {k: trim_stat(v) for k, v in d.items()}

    out["analysis"] = {}
    for enc, a in payload["analysis"].items():
        out["analysis"][enc] = dict(
            overall=trim_decomp(a["overall"]),
            overall_fallback=trim_decomp(a["overall_fallback"]),
            by_category={c: trim_decomp(v) for c, v in a["by_category"].items()},
            renyi_efficiency=a["renyi_efficiency"],
            attested_premium=trim_stat(a["attested_premium"]),
        )
    cx = []
    for c in payload["constructions"]:
        e = dict(c)
        for enc in payload["meta"]["encodings"]:
            e[enc] = dict(e[enc])
            e[enc]["canonical"] = _sanitize_pieces(e[enc]["canonical"])
            e[enc]["variant"] = _sanitize_pieces(e[enc]["variant"])
        cx.append(e)
    out["constructions"] = cx
    out["vocab_audit"] = {}
    for enc, v in payload["vocab_audit"].items():
        prof = v["profile"]
        out["vocab_audit"][enc] = dict(
            coverage=v["coverage"],
            profile=dict(n_han_tokens=prof["n_han_tokens"],
                         vocab_size=prof["vocab_size"],
                         pct_of_vocab=prof["pct_of_vocab"],
                         length_distribution=prof["length_distribution"],
                         longest=prof["longest"][:30],
                         earliest_multichar=prof["earliest_multichar"][:30]),
        )
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", default=Path("data/study.json"), type=Path)
    ap.add_argument("--template", default=Path("web/zh-tokenizer.template.html"), type=Path)
    ap.add_argument("--out", default=Path("web/zh-tokenizer.html"), type=Path)
    args = ap.parse_args()

    payload = json.loads(args.study.read_text(encoding="utf-8"))
    compact = json.dumps(jsonable(trim(payload)), ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False)
    html = args.template.read_text(encoding="utf-8")
    if "__STUDY_DATA__" not in html:
        raise SystemExit("template is missing the __STUDY_DATA__ placeholder")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html.replace("__STUDY_DATA__", compact), encoding="utf-8")
    print(f"wrote {args.out} ({args.out.stat().st_size/1024:.0f} KB, "
          f"data {len(compact)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
