"""stats.py — turning per-sentence numbers into claims you can defend.

The design is fully within-item (every item appears in all six cells), so the
right unit of analysis is the *item-level contrast*, not the pooled mean.
Three things are reported for every contrast:

  point estimate      mean of the per-item differences
  interval            95% CI by paired bootstrap over items (B = 10000)
  non-parametric test Wilcoxon signed-rank (n is small; normality is not
                      assumed, and token counts are bounded below)

and an effect size, because "+18.4% (p < .001)" says nothing about whether a
reader would notice.  We use the rank-biserial correlation, which pairs
naturally with Wilcoxon.

Factorial decomposition
-----------------------
With SCRIPT (trad/simp) x LEXICON (tw/cn/hk) crossed within item, the three
quantities of interest are

    script effect    mean over lexicons of  len(trad) - len(simp)
    lexicon effect   mean over scripts of   len(lex)  - len(cn-lexicon)
    interaction      does the lexicon effect differ by script?

The interaction is the linguistically interesting one: if the traditional
script already forces byte fallback, a lexical mismatch may cost nothing extra
(the characters were already being spelled out byte by byte), so the two
"taxes" are not additive.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Sequence

import numpy as np
from scipy import stats as sps

RNG = np.random.default_rng(20260303)


def paired_bootstrap(diffs: Sequence[float], n_boot: int = 10_000,
                     alpha: float = 0.05) -> dict:
    d = np.asarray(diffs, dtype=float)
    d = d[~np.isnan(d)]
    if len(d) == 0:
        return dict(mean=float("nan"), lo=float("nan"), hi=float("nan"), n=0)
    idx = RNG.integers(0, len(d), size=(n_boot, len(d)))
    means = d[idx].mean(axis=1)
    return dict(
        mean=float(d.mean()),
        lo=float(np.quantile(means, alpha / 2)),
        hi=float(np.quantile(means, 1 - alpha / 2)),
        n=int(len(d)),
    )


def wilcoxon(diffs: Sequence[float]) -> dict:
    d = np.asarray(diffs, dtype=float)
    d = d[~np.isnan(d)]
    nz = d[d != 0]
    if len(nz) < 3:
        return dict(stat=float("nan"), p=float("nan"), rank_biserial=float("nan"),
                    n_nonzero=int(len(nz)))
    res = sps.wilcoxon(nz, alternative="two-sided", zero_method="wilcox")
    # rank-biserial r = (W+ - W-) / (W+ + W-)
    ranks = sps.rankdata(np.abs(nz))
    wp = ranks[nz > 0].sum()
    wm = ranks[nz < 0].sum()
    rb = (wp - wm) / (wp + wm) if (wp + wm) else float("nan")
    return dict(stat=float(res.statistic), p=float(res.pvalue),
                rank_biserial=float(rb), n_nonzero=int(len(nz)))


def contrast(rows: list[dict], key: str, cond_a: dict, cond_b: dict,
             item_key: str = "item_id", relative: bool = False) -> dict:
    """Item-wise contrast between two cell selections.

    `cond_a` / `cond_b` are dicts of column->value used to pick a unique row
    per item, e.g. {"script": "trad", "lexicon": "tw"}.
    """
    by_item: dict[str, dict[str, float]] = defaultdict(dict)
    for r in rows:
        if all(r.get(k) == v for k, v in cond_a.items()):
            by_item[r[item_key]]["a"] = r[key]
        if all(r.get(k) == v for k, v in cond_b.items()):
            by_item[r[item_key]]["b"] = r[key]
    diffs, items = [], []
    for it, ab in by_item.items():
        if "a" in ab and "b" in ab:
            if relative:
                diffs.append((ab["a"] - ab["b"]) / ab["b"] if ab["b"] else float("nan"))
            else:
                diffs.append(ab["a"] - ab["b"])
            items.append(it)
    out = paired_bootstrap(diffs)
    out.update(wilcoxon(diffs))
    out["items"] = items
    out["diffs"] = [float(x) for x in diffs]
    out["metric"] = key
    out["a"] = cond_a
    out["b"] = cond_b
    out["relative"] = relative
    return out


def decompose(rows: list[dict], key: str = "n_tokens") -> dict:
    """Script effect, lexicon effect, and their interaction.

    Reference cell is (simp, cn) — the condition the training corpora of every
    major tokenizer are overwhelmingly drawn from.
    """
    lexicons = ["tw", "cn", "hk"]
    out: dict[str, dict] = {}

    # main effect of script, averaged over lexicon, item-wise
    by_item = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        by_item[r["item_id"]][r["lexicon"]][r["script"]] = r[key]
    script_diffs = []
    for it, lex_map in by_item.items():
        ds = [lex_map[l]["trad"] - lex_map[l]["simp"]
              for l in lexicons if "trad" in lex_map.get(l, {}) and "simp" in lex_map.get(l, {})]
        if ds:
            script_diffs.append(float(np.mean(ds)))
    out["script_trad_minus_simp"] = {**paired_bootstrap(script_diffs), **wilcoxon(script_diffs)}

    # main effect of lexicon (each vs cn), averaged over script
    for lex in ("tw", "hk"):
        ds = []
        for it, lex_map in by_item.items():
            vals = [lex_map[lex][s] - lex_map["cn"][s]
                    for s in ("trad", "simp")
                    if s in lex_map.get(lex, {}) and s in lex_map.get("cn", {})]
            if vals:
                ds.append(float(np.mean(vals)))
        out[f"lexicon_{lex}_minus_cn"] = {**paired_bootstrap(ds), **wilcoxon(ds)}

    # interaction: is the lexical penalty bigger in traditional script?
    for lex in ("tw", "hk"):
        ds = []
        for it, lex_map in by_item.items():
            try:
                d_trad = lex_map[lex]["trad"] - lex_map["cn"]["trad"]
                d_simp = lex_map[lex]["simp"] - lex_map["cn"]["simp"]
            except KeyError:
                continue
            ds.append(float(d_trad - d_simp))
        out[f"interaction_{lex}"] = {**paired_bootstrap(ds), **wilcoxon(ds)}

    # the naive v1 quantity, for comparison: attested cells only
    naive = []
    for it, lex_map in by_item.items():
        try:
            tw = lex_map["tw"]["trad"]
            cn = lex_map["cn"]["simp"]
        except KeyError:
            continue
        naive.append((tw - cn) / cn if cn else float("nan"))
    out["naive_v1_tw_over_cn_relative"] = paired_bootstrap(naive)
    return out


def fmt(d: dict, unit: str = "") -> str:
    p = d.get("p", float("nan"))
    pstr = "p < .001" if p == p and p < 1e-3 else f"p = {p:.3f}"
    return (f"{d['mean']:+.2f}{unit} "
            f"[{d['lo']:+.2f}, {d['hi']:+.2f}] "
            f"({pstr}, r_rb = {d.get('rank_biserial', float('nan')):.2f}, n = {d['n']})")
