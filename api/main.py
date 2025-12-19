import os
from uuid import uuid4

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException

app = FastAPI()

def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "appdb"),
        user=os.getenv("POSTGRES_USER", "app_user"),
        password=os.getenv("POSTGRES_PASSWORD", "app_pass"),
    )

def init_db():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    result TEXT,
                    status TEXT NOT NULL,
                    text   TEXT NOT NULL
                );
            """)
            conn.commit()
    finally:
        conn.close()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/tasks")
def create_task(data: dict):
    text = data.get("text")
    if not text or not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Field 'text' is required and must be a string")

    task_id = str(uuid4())
    status = "queued"

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (task_id, result, status, text) VALUES (%s, NULL, %s, %s);",
                (task_id, status, text),
            )
            conn.commit()
    finally:
        conn.close()

    return {"task_id": task_id, "status": status, "text": text}

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT task_id, result, status, text FROM tasks WHERE task_id = %s;",
                (task_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    return row
