# Task URL Platform (FastAPI + Postgres + Worker) — pet-project для DevOps

Небольшая платформа задач: API принимает задачу (`text`), сохраняет в PostgreSQL со статусом `queued`, воркер забирает задачи из БД, обрабатывает и обновляет статус до `done` + записывает результат.  
Проект упакован в Docker Compose и имеет CI на GitHub Actions (smoke-тест полного стека).

---

## Зачем этот проект (DevOps-контекст)

Цель проекта — показать практические навыки DevOps уровня стажёра/junior:

- контейнеризация сервисов (Docker)
- оркестрация локального окружения (Docker Compose)
- сетевое взаимодействие сервисов (service discovery через Compose)
- reverse proxy (Nginx как единая точка входа)
- PostgreSQL как хранилище состояния задач
- простейший background worker (паттерн “очередь задач” через БД)
- CI: сборка, запуск, smoke-тест и сбор логов (GitHub Actions)

---

## Архитектура

**Компоненты:**
- **nginx** — входная точка (порт `8080`), проксирует запросы в API
- **api (FastAPI)** — REST API, создаёт задачи и читает их статус из Postgres
- **worker (Python)** — опрашивает БД, берёт `queued` задачи, обрабатывает, пишет `result`, ставит `done`
- **db (PostgreSQL)** — хранит таблицу `tasks`

**Поток данных:**
1) Клиент → `POST /tasks` → API  
2) API → `INSERT INTO tasks(status='queued')`  
3) Worker → берёт `queued` → `running` → `done + result`  
4) Клиент → `GET /tasks/{task_id}` → API → читает из БД

---

## Структура репозитория:
```
    Task-URL-Platform/
        docker-compose.yml
        .env.example
        nginx/nginx.conf
        api/
        Dockerfile
        requirements.txt
        main.py
        worker/
        Dockerfile
        requirements.txt
        worker.py
        .github/workflows/ci.yml
```


## Запуск стека: 

Перед началом копируем .env файл:

```
    cp .env.example .env
```

```
    docker compose up -d --build
    docker compose ps
```


## Проверка работы (curl)
Входная точка через Nginx: http://localhost:8080

```
    curl -s http://localhost:8080/health
```

Ожидаемый ответ:

```
    {"status":"ok"}
```

## Создание задачи:

```
    curl -s -X POST http://localhost:8080/tasks \
    -H "Content-Type: application/json" \
    -d '{"text":"hello from api"}'
    echo
```

Пример ответа:
```
    {"task_id":"...","status":"queued","text":"hello from api"}
```

## Получение статуса задачи

```
    curl -s http://localhost:8080/tasks/<TASK_ID> # подставляем task_id
```

Через несколько секунд воркер обработает задачу:
```
    {"task_id":"...","status":"done","text":"...","result":"..."}
```

## CI (Github Actions)
CI (GitHub Actions)
В репозитории настроен CI пайплайн, который запускается на:
- push
- pull_request

Что делает CI:
1. создаёт .env прямо в раннере (без хранения секретов в репо)
2. собирает Docker образы (docker compose build)
3. поднимает стек (docker compose up -d)
4. проверяет GET /health через Nginx
5. создаёт задачу POST /tasks
6. ожидает, что воркер обработает её и статус станет done
7. при ошибке печатает логи контейнеров и корректно останавливает стек

Author: Безоян Роман