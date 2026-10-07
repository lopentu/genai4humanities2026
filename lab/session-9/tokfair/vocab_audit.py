"""Vocabulary form audit. Entries do not reveal exact training corpora,
frequencies, dates or model competence. Conversion mappings are operational,
not an exhaustive or unique traditional/simplified character inventory.
"""
from __future__ import annotations

from collections import Counter

import opencc
import regex as re

HAN_ONLY = re.compile(r"^\p{Script=Han}+$")
_T2S = opencc.OpenCC("t2s")
_S2T = opencc.OpenCC("s2t")


def han_tokens(enc) -> list[tuple[int, str]]:
    """All vocabulary entries that are pure Han strings (leading space stripped)."""
    out = []
    for b, rank in enc.ranks.items():
        try:
            s = b.decode("utf-8")
        except UnicodeDecodeError:
            continue
        t = s
        if t and HAN_ONLY.match(t):
            out.append((rank, t))
    out.sort()
    return out


def coverage_asymmetry(enc) -> dict:
    """Conditional coverage of exact single-Han byte entries under OpenCC.
    Missing standalone characters may still occur in multicharacter tokens.
    """
    chars = {t for _, t in han_tokens(enc) if len(t) == 1}
    simp_with_trad = [c for c in chars if _S2T.convert(c) != c]
    trad_with_simp = [c for c in chars if _T2S.convert(c) != c]
    missing_trad = sorted(_S2T.convert(c) for c in simp_with_trad
                          if _S2T.convert(c) not in chars)
    missing_simp = sorted(_T2S.convert(c) for c in trad_with_simp
                          if _T2S.convert(c) not in chars)
    return dict(
        n_single_han=len(chars),
        n_simp_with_distinct_trad=len(simp_with_trad),
        n_trad_counterpart_missing=len(missing_trad),
        pct_trad_counterpart_missing=(
            100 * len(missing_trad) / len(simp_with_trad) if simp_with_trad else float("nan")),
        n_trad_with_distinct_simp=len(trad_with_simp),
        n_simp_counterpart_missing=len(missing_simp),
        pct_simp_counterpart_missing=(
            100 * len(missing_simp) / len(trad_with_simp) if trad_with_simp else float("nan")),
        example_missing_trad="".join(missing_trad[:60]),
        example_missing_simp="".join(missing_simp[:60]),
    )


def length_profile(enc) -> dict:
    toks = han_tokens(enc)
    lens = Counter(len(t) for _, t in toks)
    return dict(
        n_han_tokens=len(toks),
        vocab_size=enc.vocab_size,
        pct_of_vocab=100 * len(toks) / enc.vocab_size,
        length_distribution={str(k): v for k, v in sorted(lens.items())},
        longest=[t for _, t in sorted(toks, key=lambda x: -len(x[1]))[:40]],
        # Lowest-rank multicharacter entries; not corpus frequency estimates.
        earliest_multichar=[t for _, t in toks if len(t) >= 2][:40],
    )


#: Hand-written probe list.  A student replaces this with a real classification
#: task: sample n = 200 multi-character Han tokens, have two annotators label
#: each as MORPHEME / WORD / COLLOCATION / PHRASE / FRAGMENT / SPAM, report
#: kappa.  This is a descriptive annotation study, requiring a defensible sampling frame.
UNIT_TYPE_LABELS = ["MORPHEME", "WORD", "COLLOCATION", "PHRASE", "FRAGMENT", "SPAM/BOILERPLATE"]


def sample_for_annotation(enc, n: int = 200, min_len: int = 2, seed: int = 0) -> list[str]:
    import random
    rng = random.Random(seed)
    cands = [t for _, t in han_tokens(enc) if len(t) >= min_len]
    return rng.sample(cands, min(n, len(cands)))
