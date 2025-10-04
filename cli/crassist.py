import typer, sys, json
from pathlib import Path
from backend.app.llm_client import OllamaClient
from backend.app.review_engine import run_review
from backend.app.db import init_db, save_review, fetch_review
from backend.app.config import DEFAULT_PERSONA

app = typer.Typer(help="Code Review Assistant CLI")

@app.command("submit")
def submit(diff: Path = typer.Option(..., help="Path to unified diff (or '-' to read stdin)"),
           persona: str = DEFAULT_PERSONA,
           mock: bool = True):
    """
    Submit a diff for review. Use mock=True for local dev (no Ollama).
    """
    if str(diff) == "-":
        diff_text = sys.stdin.read()
    else:
        diff_text = diff.read_text()

    client = OllamaClient(mock=mock)
    comments = run_review(diff_text, persona, client)
    init_db()
    review_id = save_review(diff_text, persona, comments, comments)
    typer.echo(f"Saved review id={review_id} with {len(comments)} comments")

@app.command("history")
def history():
    import sqlite3
    from backend.app.config import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, created_at, reviewer_persona FROM reviews ORDER BY id DESC LIMIT 50")
    rows = cur.fetchall()
    for r in rows:
        typer.echo(f"{r[0]} | {r[1]} | {r[2]}")
    conn.close()

@app.command("show")
def show(review_id: int):
    r = fetch_review(review_id)
    if not r:
        typer.echo("Not found")
        raise typer.Exit(code=1)
    typer.echo(json.dumps(r, indent=2))

if __name__ == "__main__":
    app()
