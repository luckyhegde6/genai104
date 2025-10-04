# Low-Level Design
## Project layout

```
code-review-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry
│   │   ├── api/
│   │   │   └── reviews.py       # endpoints
│   │   ├── models.py            # pydantic & ORM
│   │   ├── db.py                # sqlite connection + migrations simple
│   │   ├── llm_client.py        # Ollama wrapper
│   │   ├── review_engine.py     # parsing + prompt building + parse result
│   │   └── config.py
│   ├── tests/
│   └── requirements.txt
├── cli/
│   └── crassist.py              # Typer CLI: submit-diff, history, fetch
├── hooks/
│   └── pre-commit               # example git hook that calls CLI
├── docs/
│   └── architecture.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── README.md
└── examples/
    ├── sample_diff.patch
    └── sample_review.json
```
## Data model (SQLite
Tables:

- reviews

    - id INTEGER PRIMARY KEY

    - created_at DATETIME

    - diff_text TEXT

    - reviewer_persona TEXT

    - severity_summary TEXT (cached)

    - raw_llm_response TEXT

- review_comments

    - id INTEGER PRIMARY KEY

    - review_id REFERENCES reviews(id)

    - file_path TEXT

    - line_start INTEGER

    - line_end INTEGER

    - category TEXT (readability, perf, security, style)

    - severity TEXT (low/medium/high)

    - message TEXT

    - suggestion TEXT

## Core modules
- llm_client.py

Responsibility: run Ollama model locally and return text. Minimal interface:

```python
class OllamaClient:
    def __init__(model_name: str = "gemma3:4b", timeout: int = 30):
        ...
    def run_prompt(self, prompt: str) -> str:
        # uses subprocess: `ollama run <model> --prompt '<prompt>'`
```

- ## review_engine.py

### Responsibility:

Parse unified diff or git patch to structured file+chunk changes (use python-diff-parser or a custom parser).

Build prompt: include persona settings, constraints to output JSON with fields [file, start, end, category, severity, message, suggestion].

Call llm_client.run_prompt and parse JSON (prefer JSON output to reduce hallucination).

Validate and store comments in DB.

Important: Force LLM to produce JSON only by including exact system instruction and post-validate.

- ## api/reviews.py (FastAPI)

### Endpoints:

POST /reviews — body: { "diff": "...", "persona": "strict" } → starts immediate review and returns review id + comments

GET /reviews/{id} — get stored review + comments

GET /reviews — list recent reviews

- ## CLI (typer)

### Commands:

crassist submit --diff file.patch --persona mentor -> posts to backend or calls review_engine directly (local mode).

crassist history -> list local reviews

crassist show <id> -> print structured review

- ## Git Hook

pre-commit script reads staged diff git diff --cached or git diff --staged --name-only and runs crassist submit --diff - (support reading from stdin). Use --persona strict in CI sim.