import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

POLL_SECONDS = 2

def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "appdb"),
        user=os.getenv("POSTGRES_USER", "app_user"),
        password=os.getenv("POSTGRES_PASSWORD", "app_pass"),
    )

def process_text(text: str) -> str:
    return f"len={len(text)}; upper={text.upper()}"

def main():
    print("worker started")
    while True:
        conn = get_conn()
        try:
            # Берём 1 queued задачу с блокировкой, чтобы в будущем можно было масштабировать воркеры
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT task_id, text
                    FROM tasks
                    WHERE status = 'queued'
                    ORDER BY task_id
                    LIMIT 1
                    FOR UPDATE SKIP LOCKED;
                """)
                row = cur.fetchone()

                if not row:
                    conn.commit()
                    time.sleep(POLL_SECONDS)
                    continue

                task_id = row["task_id"]
                text = row["text"]

                cur.execute("UPDATE tasks SET status='running' WHERE task_id=%s;", (task_id,))
                conn.commit()

            # "работа"
            result = process_text(text)

            with conn.cursor() as cur2:
                cur2.execute(
                    "UPDATE tasks SET status='done', result=%s WHERE task_id=%s;",
                    (result, task_id),
                )
                conn.commit()

            print(f"processed {task_id} -> done")

        except Exception as e:
            print("worker error:", e)
            time.sleep(POLL_SECONDS)
        finally:
            conn.close()

if __name__ == "__main__":
    main()
