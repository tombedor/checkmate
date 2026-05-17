set shell := ["zsh", "-cu"]

default:
  @just --list

run pgn username="" games="100" stockfish="stockfish":
  @python_bin=".venv/bin/python"; \
  if [[ ! -x "$python_bin" ]]; then python_bin="python3"; fi; \
  cmd=("$python_bin" run.py --pgn {{pgn}} --games {{games}} --stockfish {{stockfish}}); \
  if [[ -n "{{username}}" ]]; then cmd+=(--username "{{username}}"); fi; \
  "${cmd[@]}"

serve port="8000":
  @python_bin=".venv/bin/python"; \
  if [[ ! -x "$python_bin" ]]; then python_bin="python3"; fi; \
  "$python_bin" serve.py --port {{port}}

browser-test:
  @python_bin=".venv/bin/python"; \
  if [[ ! -x "$python_bin" ]]; then python_bin="python3"; fi; \
  "$python_bin" -m pytest tests

browser-screenshot url="http://127.0.0.1:8000/" output_dir="output/test-artifacts":
  @python_bin=".venv/bin/python"; \
  if [[ ! -x "$python_bin" ]]; then python_bin="python3"; fi; \
  "$python_bin" scripts/capture_study_screenshots.py --url {{url}} --output-dir {{output_dir}}

inspect-puzzle puzzle_id:
  @python_bin=".venv/bin/python"; \
  if [[ ! -x "$python_bin" ]]; then python_bin="python3"; fi; \
  "$python_bin" scripts/inspect_puzzle.py {{puzzle_id}}
