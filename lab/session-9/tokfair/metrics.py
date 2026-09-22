"""metrics.py — the measurement layer.

Every metric here is either (a) standard in the tokenizer-evaluation
literature, or (b) explicitly defined so a student can argue with it.  The
point of the exercise is that "token count" on its own is not a finding; a
finding needs a metric with a denominator, a baseline, and an interval.

Metrics
-------
n_tokens                raw sequence length
tokens_per_char         length normalised by Han character count
bytes_per_token         compression rate (higher = better compression)
byte_fallback_rate      share of emitted tokens that are NOT valid UTF-8 on
                        their own, i.e. raw byte fragments of a character the
                        vocabulary does not cover.  This is the *mechanism*
                        behind most of the script effect, and it is what makes
                        the effect a coverage problem rather than a
                        frequency problem.
char_integrity          share of Han characters realised as exactly one token
fertility               n_tokens / n_words, with words from a segmenter
                        (jieba here; swap in CKIP for Traditional Chinese).
                        Cf. Rust et al. (2021).
boundary_f1             agreement between token boundaries and word boundaries
                        — the same quantity used in week 2 to compare
                        segmentation standards, now applied to a tokenizer as
                        if it were one more annotation standard.
parity / premium        Petrov et al. (2023): for semantically equivalent s_A,
                        s_B, parity(A,B) = |t(s_A)| / |t(s_B)|.  premium =
                        parity - 1, i.e. the proportional surcharge A pays.
renyi_efficiency        Zouhar et al. (2023): H_alpha(token distribution) /
                        log |V_used|, alpha = 2.5.  Corpus-level; penalises
                        vocabularies whose probability mass concentrates on a
                        few tokens.

Citations in this file are from memory and have NOT been verified against the
published record — check every one before it goes on a slide.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Iterable, Sequence

import regex as re

HAN = re.compile(r"\p{Script=Han}")

try:  # optional: only needed for fertility / boundary_f1
    import jieba

    jieba.setLogLevel(60)
    _HAS_JIEBA = True
except Exception:  # pragma: no cover
    _HAS_JIEBA = False


# --------------------------------------------------------------------------
# per-text metrics
# --------------------------------------------------------------------------
def n_han(text: str) -> int:
    return len(HAN.findall(text))


def token_spans(enc, text: str) -> list[tuple[int, int]]:
    """Character offsets of each token, skipping tokens that are byte fragments.

    A multi-byte character split across several byte tokens contributes one
    span for the whole character, so boundary metrics stay well defined.
    """
    spans: list[tuple[int, int]] = []
    ids = enc.encode(text)
    buf = b""
    start = 0
    consumed = 0
    for tid in ids:
        buf += enc._inv[tid]
        try:
            piece = buf.decode("utf-8")
        except UnicodeDecodeError:
            continue  # incomplete character: keep accumulating
        consumed += len(piece)
        spans.append((start, consumed))
        start = consumed
        buf = b""
    return spans


def boundaries(spans: Sequence[tuple[int, int]]) -> set[int]:
    """Internal boundary positions (exclude string start/end)."""
    return {e for _, e in spans[:-1]} if spans else set()


def word_spans(text: str) -> list[tuple[int, int]]:
    if not _HAS_JIEBA:
        raise RuntimeError("jieba not installed; fertility/boundary_f1 unavailable")
    spans, i = [], 0
    for w in jieba.cut(text, cut_all=False):
        spans.append((i, i + len(w)))
        i += len(w)
    return spans


def boundary_f1(pred: set[int], gold: set[int]) -> float:
    """Identical in form to the week-2 inter-standard agreement measure."""
    if not pred and not gold:
        return 1.0
    tp = len(pred & gold)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(gold) if gold else 0.0
    return 0.0 if p + r == 0 else 2 * p * r / (p + r)


def text_metrics(enc, text: str, use_jieba: bool = True) -> dict:
    ids = enc.encode(text)
    n_tok = len(ids)
    n_fb = sum(enc.is_byte_fallback(i) for i in ids)
    chars = n_han(text)
    nbytes = len(text.encode("utf-8"))
    spans = token_spans(enc, text)
    single = sum(1 for a, b in spans if b - a == 1 and HAN.match(text[a:b] or " "))
    out = dict(
        text=text,
        n_tokens=n_tok,
        n_han=chars,
        n_bytes=nbytes,
        tokens_per_char=(n_tok / chars) if chars else float("nan"),
        bytes_per_token=(nbytes / n_tok) if n_tok else float("nan"),
        byte_fallback_rate=(n_fb / n_tok) if n_tok else 0.0,
        n_byte_fallback=n_fb,
        char_integrity=(single / chars) if chars else float("nan"),
    )
    if use_jieba and _HAS_JIEBA:
        ws = word_spans(text)
        out["n_words"] = len(ws)
        out["fertility"] = n_tok / len(ws) if ws else float("nan")
        out["boundary_f1"] = boundary_f1(boundaries(spans), boundaries(ws))
    return out


# --------------------------------------------------------------------------
# pairwise / corpus metrics
# --------------------------------------------------------------------------
def parity(len_a: int, len_b: int) -> float:
    """Petrov et al. (2023): ratio of token counts on equivalent content."""
    return len_a / len_b if len_b else float("nan")


def premium(len_a: int, len_b: int) -> float:
    """Proportional surcharge of A over B (0 = parity)."""
    return parity(len_a, len_b) - 1.0


def renyi_efficiency(all_ids: Iterable[int], alpha: float = 2.5) -> float:
    """Zouhar et al. (2023), 'Tokenization and the Noiseless Channel'.

    Reported as H_alpha / log |V_used| so that it lies in (0, 1] and is
    comparable across corpora of different vocabulary usage.
    """
    counts = Counter(all_ids)
    total = sum(counts.values())
    if total == 0 or len(counts) < 2:
        return float("nan")
    ps = [c / total for c in counts.values()]
    if abs(alpha - 1.0) < 1e-9:
        h = -sum(p * math.log(p) for p in ps)
    else:
        h = math.log(sum(p ** alpha for p in ps)) / (1 - alpha)
    return h / math.log(len(counts))


# --------------------------------------------------------------------------
# what the numbers cost
# --------------------------------------------------------------------------
#: USD per 1M input tokens.  PLACEHOLDER — vendor pricing changes constantly,
#: so verify before use.  Kept in one place so a student can update it.
PRICE_USD_PER_MTOK = {"cl100k_base": 2.50, "o200k_base": 2.50}
#: nominal context window in tokens, same caveat
CONTEXT_TOKENS = {"cl100k_base": 128_000, "o200k_base": 128_000}


def cost_and_context(enc_name: str, tokens_per_char: float) -> dict:
    """Translate a rate into the two things a user actually experiences."""
    price = PRICE_USD_PER_MTOK.get(enc_name)
    ctx = CONTEXT_TOKENS.get(enc_name)
    return dict(
        usd_per_million_chars=(price * tokens_per_char if price else None),
        chars_in_context=(ctx / tokens_per_char if ctx and tokens_per_char else None),
    )
