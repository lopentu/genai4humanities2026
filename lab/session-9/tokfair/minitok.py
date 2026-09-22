"""minitok — a dependency-light, offline re-implementation of tiktoken's encoder.

Why this exists
---------------
`tiktoken` downloads its BPE rank tables from an OpenAI blob endpoint at first
use.  In a locked-down classroom / CI environment that call fails.  The npm
package `js-tiktoken` ships the *same* rank tables as plain files, so we parse
those instead and re-implement the (very short) encoding algorithm.

Anything produced here is byte-identical to `tiktoken.get_encoding(name)`.

Usage
-----
    enc = MiniTok.from_ranks_file("ranks/cl100k_base.js")
    ids = enc.encode("這個軟體更新了介面。")
    enc.decode_single(ids[0])
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path

import regex as re  # `regex`, not `re`: we need \p{L} / \p{N} Unicode properties


def _parse_js_ranks(path: str | Path) -> dict:
    """Read a js-tiktoken `ranks/*.js` file and return the raw JSON payload."""
    text = Path(path).read_text(encoding="utf-8")
    start = text.index("{")
    end = text.rindex("}") + 1
    return json.loads(text[start:end])


def _decompress_bpe_ranks(compressed: str) -> dict[bytes, int]:
    """js-tiktoken stores ranks as newline-separated run-length blocks.

    Each line is `<ignored> <offset> <b64tok> <b64tok> ...`; the i-th token on
    the line has rank `offset + i`.
    """
    ranks: dict[bytes, int] = {}
    for line in compressed.split("\n"):
        if not line:
            continue
        parts = line.split(" ")
        offset = int(parts[1])
        for i, tok in enumerate(parts[2:]):
            ranks[base64.b64decode(tok)] = offset + i
    return ranks


@dataclass
class MiniTok:
    name: str
    pat_str: str
    ranks: dict[bytes, int]
    special_tokens: dict[str, int] = field(default_factory=dict)

    _pat: re.Pattern = field(init=False, repr=False)
    _inv: dict[int, bytes] = field(init=False, repr=False)
    _cache: dict = field(init=False, repr=False, default_factory=dict)

    def __post_init__(self):
        self._pat = re.compile(self.pat_str)
        self._inv = {v: k for k, v in self.ranks.items()}
        self._cache = {}

    # ---- construction -------------------------------------------------
    @classmethod
    def from_ranks_file(cls, path: str | Path, name: str | None = None) -> "MiniTok":
        payload = _parse_js_ranks(path)
        return cls(
            name=name or Path(path).stem,
            pat_str=payload["pat_str"],
            ranks=_decompress_bpe_ranks(payload["bpe_ranks"]),
            special_tokens=payload.get("special_tokens", {}),
        )

    @property
    def vocab_size(self) -> int:
        return len(self.ranks) + len(self.special_tokens)

    # ---- core BPE -----------------------------------------------------
    def _merge(self, piece: bytes) -> list[bytes]:
        """Greedy lowest-rank-first pair merging (tiktoken's `byte_pair_merge`)."""
        if len(piece) == 1:
            return [piece]
        parts = [(i, i + 1) for i in range(len(piece))]
        while len(parts) > 1:
            best_rank, best_i = None, None
            for i in range(len(parts) - 1):
                cand = piece[parts[i][0]: parts[i + 1][1]]
                r = self.ranks.get(cand)
                if r is None:
                    continue
                if best_rank is None or r < best_rank:
                    best_rank, best_i = r, i
            if best_i is None:
                break
            parts[best_i] = (parts[best_i][0], parts[best_i + 1][1])
            del parts[best_i + 1]
        return [piece[a:b] for a, b in parts]

    def _encode_piece(self, piece: bytes) -> tuple[int, ...]:
        hit = self._cache.get(piece)
        if hit is not None:
            return hit
        if piece in self.ranks:
            out = (self.ranks[piece],)
        else:
            out = tuple(self.ranks[p] for p in self._merge(piece) if p in self.ranks)
        self._cache[piece] = out
        return out

    # ---- public API ---------------------------------------------------
    def pretokenize(self, text: str) -> list[str]:
        """The regex pre-tokenizer: BPE is never allowed to merge across these."""
        return [m.group(0) for m in self._pat.finditer(text)]

    def encode(self, text: str) -> list[int]:
        out: list[int] = []
        for m in self.pretokenize(text):
            out.extend(self._encode_piece(m.encode("utf-8")))
        return out

    def decode_bytes(self, ids: list[int]) -> bytes:
        return b"".join(self._inv[i] for i in ids)

    def decode(self, ids: list[int]) -> str:
        return self.decode_bytes(ids).decode("utf-8", errors="replace")

    def pieces(self, text: str) -> list[str]:
        """One surface string per token (invalid UTF-8 shown with U+FFFD)."""
        return [self._inv[i].decode("utf-8", errors="replace") for i in self.encode(text)]

    def is_byte_fallback(self, tid: int) -> bool:
        """True if this token id is not a valid standalone UTF-8 string.

        A CJK character that the vocabulary does not cover is emitted as 2-3
        raw UTF-8 byte tokens; each of those is a byte-fallback token.
        """
        try:
            self._inv[tid].decode("utf-8")
            return False
        except UnicodeDecodeError:
            return True


def load_bundled(rank_dir: str | Path, names=("cl100k_base", "o200k_base")) -> dict[str, MiniTok]:
    rank_dir = Path(rank_dir)
    return {n: MiniTok.from_ranks_file(rank_dir / f"{n}.js", name=n) for n in names}
