#!/usr/bin/env bash
# Start the live-cell server and the deck preview together (WSL, conda env "census").
# Ctrl+C stops both.
set -e
cd "$(dirname "$0")"
eval "$(conda shell.bash hook)"
conda activate census

python live.py &
LIVE=$!
trap 'kill $LIVE 2>/dev/null' EXIT

echo "Waiting for live.py to finish warm-up..."
until curl -s -o /dev/null http://localhost:5006/cell; do
  kill -0 $LIVE 2>/dev/null || { echo "live.py exited, see the error above"; exit 1; }
  sleep 2
done

quarto preview lecture.qmd --no-browser
