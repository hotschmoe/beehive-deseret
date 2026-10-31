#!/usr/bin/env bash
cd "$(dirname "$0")/docs" && exec python3 -m http.server "${1:-8420}" --bind 0.0.0.0
