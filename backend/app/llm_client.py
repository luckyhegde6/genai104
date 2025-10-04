import subprocess, shlex, json, os, time
from .config import OLLAMA_MODEL, MOCK_LLM

class OllamaClient:
    """
    Minimal wrapper around `ollama run` with a mock mode (for CI/dev).
    """
    def __init__(self, model_name: str = None, mock: bool = None, timeout: int = 60):
        self.model = model_name or OLLAMA_MODEL
        self.timeout = timeout
        # Allow explicit override but default to config
        self.mock = MOCK_LLM if mock is None else mock

    def run_prompt(self, prompt: str) -> str:
        if self.mock:
            # return predictable JSON array as string for dev/testing
            return json.dumps([{
                "file_path": "src/app.py",
                "line_start": 10,
                "line_end": 12,
                "category": "readability",
                "severity": "low",
                "message": "Consider renaming variable 'x' to 'user_count'.",
                "suggestion": "rename x -> user_count"
            }])
        # run local ollama
        cmd = f"ollama run {shlex.quote(self.model)} --prompt {shlex.quote(prompt)}"
        try:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=self.timeout)
            if proc.returncode != 0:
                raise RuntimeError(f"Ollama error: {proc.stderr.strip()}")
            return proc.stdout
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("Ollama timed out") from e
