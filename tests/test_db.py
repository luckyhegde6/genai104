from backend.app.db import init_db, save_review, fetch_review, get_conn
import os

def test_db_save_and_fetch(tmp_path):
    # use a temp DB path
    db_file = tmp_path / "test_reviews.db"
    os.environ["REVIEWS_DB_PATH"] = str(db_file)
    init_db()
    comments = [{
        "file_path":"a.py","line_start":1,"line_end":2,"category":"style",
        "severity":"low","message":"msg","suggestion":"sugg"
    }]
    rid = save_review("diff", "mentor", str(comments), comments)
    r = fetch_review(rid)
    assert r["id"] == rid
    assert len(r["comments"]) == 1
