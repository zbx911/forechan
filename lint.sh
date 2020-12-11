#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname "$0")" || exit 1

FILES=(
  forechan/*.py
)

mypy -- "${FILES[@]}"