from backend.app.review_engine import run_review
from backend.app.llm_client import OllamaClient

def test_run_review_mock():
    diff = "diff --git a/src/app.py b/src/app.py\n@@ -1 +1 @@\n-hello\n+world\n"
    client = OllamaClient(mock=True)
    res = run_review(diff, "mentor", client)
    assert isinstance(res, list)
    assert len(res) >= 1
    assert "file_path" in res[0]
