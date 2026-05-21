#!/usr/bin/env bash

set -euo pipefail

. .env

# Random env vars generated during worktree init
echo "FOO: $FOO"
echo "BAR: $BAR"

# Dummy server start log, just for demonstration
echo "Starting server on port $PORT..."
