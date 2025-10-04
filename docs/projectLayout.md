# Project Layout
The project is organized into the following structure:

```
code-review-assistant/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api_reviews.py
│   │   ├── llm_client.py
│   │   ├── review_engine.py
│   │   ├── db.py
│   │   └── config.py
│   └── requirements.txt
├── cli/
│   └── crassist.py
├── hooks/
│   └── pre-commit
├── .github/
│   └── workflows/
│       └── ci.yml
├── tests/
│   ├── test_review_engine.py
│   └── test_db.py
├── examples/
│   └── sample_diff.patch
└── README.md
```
