from fastapi import FastAPI
from uuid import uuid4

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/task")
def create_task(data: dict):
    text = data.get("text", "")
    task_id = str(uuid4())
    return {"task_id": task_id, "status": "queued", "text": text}
