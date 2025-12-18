from fastapi import FastAPI, HTTPException
from uuid import uuid4

app = FastAPI()

# Хранилище в памяти (пока без БД)
# key = task_id, value = данные задачи
tasks = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks")
def create_task(data: dict):
    # 1) Достаём text из JSON
    text = data.get("text")

    # 2) Простая валидация
    if not text or not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Field 'text' is required and must be a string")

    # 3) Генерируем id
    task_id = str(uuid4())

    # 4) Сохраняем задачу в памяти
    tasks[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "text": text
    }

    # 5) Возвращаем результат
    return tasks[task_id]


@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    # Если задачи нет — 404
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
