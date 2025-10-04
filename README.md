# genai104

# Code Review Assistant (Local + Offline)

A local CLI + optional web API that takes a PR diff and produces structured code review comments powered by a local LLM (Ollama).

## Highlights
- Structured reviews: severity, category, file/line ranges, suggestion.
- Configurable reviewer persona: `strict` | `mentor` | `balanced`.
- Works offline with Ollama models: `gemma3:4b`, `qwen3:4b`, `deepseek-r1`.
- Stores review history in SQLite.
- Integrates as a Git hook (pre-commit or local CI simulation).
- CI-friendly: tests mock LLM responses to keep pipeline fast.

## Quickstart (local)
### Prereqs
- Python 3.10+
- Ollama installed & model pulled (optional for dev; CI uses mock)
  - Example: `ollama pull gemma3:4b`
- git

### Install
```bash
git clone <repo>
cd code-review-assistant/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "from app.db import init_db; init_db()"

### Run FastAPI backend (optional)
```
uvicorn app.main:app --reload --port 8000
```

### CLI usage (local mode)
```bash
# from repo root
python -m cli.crassist submit --diff examples/sample_diff.patch --persona mentor
python -m cli.crassist history
python -m cli.crassist show 1
```

### Git Hook
```
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
This will call crassist submit on staged diffs (non-blocking by default).

### CI Mode (mock LLM)
The included GitHub Actions workflow runs tests and lints and uses a mocked LLM (no heavy model needed). If you want to run with a real Ollama model in CI, configure a self-hosted runner that has Ollama and the model.

## Docs

### How it works (short)

You submit a unified diff (from git diff or PR patch).

The engine builds a structured prompt with persona, asks the local LLM.

The LLM returns JSON with review comments.

The assistant validates and persists the review.

### Tuning & Safety

Encourage the model to output strict JSON only to reduce parsing errors.

Add length limits and timeout to ollama calls.

For security, restrict the CLI to local use (do not expose the API publicly without auth).

### Contributing

Add unit tests under backend/app/tests.

Use python -m pytest in CI.

##  Git hook example
```bash
#!/usr/bin/env bash
# simple pre-commit hook: non-blocking, shows suggestions
set -e
# get staged diff
diff=$(git diff --cached)
if [ -z "$diff" ]; then
  exit 0
fi

# call the CLI in non-blocking way
python -m cli.crassist submit --diff - --persona strict <<EOF
$diff
EOF

# note: optionally fail the commit if severe issues found; keep optional for UX
exit 0
```

### Step-by-step: local setup & run
- Install Ollama (if you plan to run the real model locally)
    - Follow Ollama docs for your OS.
    - Pull a model: ollama pull gemma3:4b (or qwen3:4b / deepseek-r1:1.5b) — these are examples; ensure you have disk & RAM for gemma3:4b.

- Clone repo & create venv:
```bash
git clone <repo>
cd code-review-assistant/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "from app.db import init_db; init_db()"
```
- Init DB:
```bash
python -c "from app.db import init_db; init_db()"
```

- Try the CLI with mock LLM (no Ollama needed):
```bash
python -m cli.crassist submit --diff examples/sample_diff.patch --persona mentor --mock
python -m cli.crassist history
python -m cli.crassist show 1
```

- Try with real Ollama:

Ensure Ollama is running and model downloaded.

Run CLI without --mock (or set model via env): OLLAMA_MODEL=gemma3:4b python -m cli.crassist submit --diff examples/sample_diff.patch --persona strict

- Optional: Run backend API
```bash
uvicorn app.main:app --reload --port 8000
# then curl
curl -X POST http://127.0.0.1:8000/reviews -d '{"diff":"<your diff>", "persona":"mentor"}' -H "Content-Type: application/json"
```

# 1. Create virtualenv and install deps
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# 2. Initialize DB
python - <<'PY'
from backend.app.db import init_db
init_db()
print("DB initialized.")
PY

# 3. Run tests
pytest -q

# 4. Try the CLI (mock mode - safe, no ollama required)
python -m cli.crassist submit --diff examples/sample_diff.patch --persona mentor --mock true

# 5. List history and show review 1
python -m cli.crassist history
python -m cli.crassist show 1

# 6. (Optional) Run FastAPI
uvicorn backend.app.main:app --reload --port 8000
# then
# curl -X POST "http://127.0.0.1:8000/reviews" -H "Content-Type: application/json" -d '{"diff":"<your diff>", "persona":"mentor", "mock":true}'