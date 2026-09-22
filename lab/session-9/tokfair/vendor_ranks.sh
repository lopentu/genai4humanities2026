#!/usr/bin/env bash
# Fetch offline BPE rank tables from the js-tiktoken npm package.
# tiktoken itself downloads ranks from an OpenAI blob endpoint at first use,
# which fails behind a proxy or in CI; js-tiktoken ships the same tables as
# plain files, so we vendor those instead.
set -euo pipefail
VERSION="${1:-1.0.15}"
mkdir -p ranks && cd ranks
npm pack "js-tiktoken@${VERSION}" >/dev/null
tar xzf "js-tiktoken-${VERSION}.tgz" package/dist/ranks
mv package/dist/ranks/*.js . 2>/dev/null || true
rm -rf package "js-tiktoken-${VERSION}.tgz"
ls -la *.js
