#!/usr/bin/env bash
# Ground truth for the "vectorist" engine. Exit 0 = objective achieved.
cd "$(dirname "$0")/../.." || exit 1
node forge/build.mjs tasks/vectorist || exit 1
node forge/verify.mjs tasks/vectorist
