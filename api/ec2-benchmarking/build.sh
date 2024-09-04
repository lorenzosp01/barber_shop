#!/bin/sh --
set -e

compile_go() {
  if [ -z "$1" ]; then
    echo "Go file to compile not specified." >&2
    exit 1
  fi

  go build "$1"

  EXEC_FILE="$(basename "$1" .go)"
  strip "$EXEC_FILE"
  upx -q "$EXEC_FILE"
}

set -x

compile_go scripts/benchmark/benchmark.go
compile_go scripts/user-simulation/user-simulation.go