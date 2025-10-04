import sqlite3, datetime
from .config import DB_PATH

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        diff_text TEXT,
        reviewer_persona TEXT,
        raw_llm_response TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS review_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        review_id INTEGER,
        file_path TEXT,
        line_start INTEGER,
        line_end INTEGER,
        category TEXT,
        severity TEXT,
        message TEXT,
        suggestion TEXT,
        FOREIGN KEY(review_id) REFERENCES reviews(id)
    )""")
    conn.commit()
    conn.close()

def save_review(diff_text: str, persona: str, raw_response: str, comments: list):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO reviews(created_at,diff_text,reviewer_persona,raw_llm_response) VALUES (?,?,?,?)",
                (datetime.datetime.utcnow().isoformat(), diff_text, persona, str(raw_response)))
    review_id = cur.lastrowid
    for c in comments:
        cur.execute("""INSERT INTO review_comments(review_id,file_path,line_start,line_end,category,severity,message,suggestion)
                    VALUES (?,?,?,?,?,?,?,?)""",
                    (review_id, c.get("file_path"), c.get("line_start"), c.get("line_end"),
                     c.get("category"), c.get("severity"), c.get("message"), c.get("suggestion")))
    conn.commit()
    conn.close()
    return review_id

def fetch_review(review_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, created_at, diff_text, reviewer_persona, raw_llm_response FROM reviews WHERE id = ?", (review_id,))
    rev = cur.fetchone()
    if not rev:
        conn.close()
        return None
    cur.execute("SELECT file_path,line_start,line_end,category,severity,message,suggestion FROM review_comments WHERE review_id = ?",
                (review_id,))
    comments = [dict(zip(["file_path","line_start","line_end","category","severity","message","suggestion"], row)) for row in cur.fetchall()]
    conn.close()
    return {
        "id": rev[0],
        "created_at": rev[1],
        "diff_text": rev[2],
        "reviewer_persona": rev[3],
        "raw_llm_response": rev[4],
        "comments": comments
    }
