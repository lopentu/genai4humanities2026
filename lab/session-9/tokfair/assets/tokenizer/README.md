# Browser tokenizer bundle

Sources: js-tiktoken@1.0.15 (https://github.com/dqbd/tiktoken), base64-js via npm lockfile; MIT license notices in LICENSES.txt. esbuild@0.25.12 is a build-time dependency only. The bundle includes cl100k_base and o200k_base tables. entry.mjs exposes byte evidence using textMap; encode treats special-looking strings as ordinary text. No input is transmitted.

Rebuild: `npm ci && npm run build`. Browser/Python checks compare every precomputed row. Decoder uses fatal UTF-8 validity and preserves BOM; byte reconstruction is checked independently of decoded text.

Python and JavaScript use UTF-8 byte intervals; browser decoder preserves BOM.
