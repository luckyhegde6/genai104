# High-Level Design

## System components:

- Frontend (optional small web UI) — React (optional): submits diffs / shows reviews.

- API Backend — FastAPI: accepts PR diffs, starts review jobs, returns results, stores history in SQLite.

- CLI — Typer: local CLI to submit diff files and fetch history.

- LLM Adapter — wrapper that calls Ollama local model (gemma3:4b / qwen3:4b / deepseek-r1).

- Review Engine — pipeline that: parses diff → creates structured review prompts → calls LLM → parses response → stores structured review.

- Persistence — SQLite (history table).

- Git Hooks — pre-commit or pre-push hook which calls CLI to get lint-like suggestions.

- CI — GitHub Actions: runs tests, lint, and runs the “review engine” in mocked mode to verify integration without needing heavy local model.

## Mermaid architecture:
```mermaid
flowchart LR
  subgraph LocalMachine
    A[CLI (typer) / Web UI (optional)]
    B[FastAPI Backend]
    C[SQLite DB]
    D[Git Hooks]
    E[Ollama Runtime]
  end

  A -->|HTTP / CLI| B
  B -->|SQL| C
  B -->|Invoke| E
  D -->|exec CLI| A
  E -->|model: gemma3 / qwen3 / deepseek| B
  B -->|structured reviews| C

    subgraph CI
        F[GitHub Actions]
    end
    F -->|mock LLM| B
    F -->|runs tests/lint| B
```

