import os
import platform
import socket
from collections.abc import Mapping
from datetime import datetime

import psycopg
import redis
from flask import Flask, jsonify, redirect, render_template_string, request, url_for
from psycopg.rows import dict_row


app = Flask(__name__)

POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname": os.getenv("POSTGRES_DB", "notes"),
    "user": os.getenv("POSTGRES_USER", "notes"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "connect_timeout": 3,
}

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=0,
    socket_connect_timeout=3,
    socket_timeout=3,
    decode_responses=True,
)

PAGE_TEMPLATE = """
<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Заметки</title>
    <style>
      body { max-width: 850px; margin: 2rem auto; padding: 0 1rem; font-family: sans-serif; }
      textarea { box-sizing: border-box; min-height: 6rem; width: 100%; }
      button { margin-top: .5rem; padding: .5rem 1rem; }
      li { margin-bottom: .75rem; }
      pre { overflow-x: auto; padding: 1rem; background: #f3f3f3; }
      .meta { color: #666; font-size: .85rem; }
    </style>
  </head>
  <body>
    <h1>Заметки в контейнере</h1>
    <p>Просмотров главной страницы: <strong>{{ visits }}</strong></p>

    <h2>Новая заметка</h2>
    <form action="{{ url_for('create_note') }}" method="post">
      <textarea name="body" maxlength="2000" required></textarea>
      <br>
      <button type="submit">Сохранить</button>
    </form>

    <h2>Сохранённые заметки</h2>
    {% if notes %}
      <ol>
        {% for note in notes %}
          <li>
            {{ note.body }}
            <div class="meta">ID {{ note.id }}, {{ note.created_at }}</div>
          </li>
        {% endfor %}
      </ol>
    {% else %}
      <p>Заметок пока нет.</p>
    {% endif %}

    <h2>Информация о системе</h2>
    <pre>Hostname:       {{ info.hostname }}
OS:             {{ info.os }}
OS release:     {{ info.os_release }}
Architecture:   {{ info.architecture }}
Python version: {{ info.python_version }}
Processor:      {{ info.processor }}
PID:            {{ info.pid }}
Working dir:    {{ info.working_dir }}
Container host: {{ info.container_host }}</pre>
  </body>
</html>
"""


def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "processor": platform.processor() or "N/A",
        "pid": os.getpid(),
        "working_dir": os.getcwd(),
        "container_host": os.getenv("HOSTNAME", "N/A"),
    }


def get_db_connection():
    return psycopg.connect(**POSTGRES_CONFIG, row_factory=dict_row)


def ensure_notes_table():
    with get_db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id BIGSERIAL PRIMARY KEY,
                body TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def get_notes():
    ensure_notes_table()
    with get_db_connection() as connection:
        return connection.execute(
            """
            SELECT id, body, created_at
            FROM notes
            ORDER BY id DESC
            """
        ).fetchall()


def serialize_note(note):
    created_at = note["created_at"]
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()

    return {
        "id": note["id"],
        "body": note["body"],
        "created_at": created_at,
    }


@app.get("/")
def index():
    visits = redis_client.incr("visits")
    notes = get_notes()
    return render_template_string(
        PAGE_TEMPLATE,
        info=get_system_info(),
        notes=notes,
        visits=visits,
    )


@app.get("/notes")
def list_notes():
    return jsonify([serialize_note(note) for note in get_notes()])


@app.post("/notes")
def create_note():
    data = request.get_json(silent=True) if request.is_json else request.form
    if not isinstance(data, Mapping):
        return jsonify({"error": "Тело запроса должно быть JSON-объектом"}), 400

    body = str(data.get("body", "")).strip()

    if not body:
        return jsonify({"error": "Поле body не должно быть пустым"}), 400
    if len(body) > 2000:
        return jsonify({"error": "Заметка не должна превышать 2000 символов"}), 400

    ensure_notes_table()
    with get_db_connection() as connection:
        note = connection.execute(
            """
            INSERT INTO notes (body)
            VALUES (%s)
            RETURNING id, body, created_at
            """,
            (body,),
        ).fetchone()

    if request.is_json:
        return jsonify(serialize_note(note)), 201
    return redirect(url_for("index"), code=303)


@app.get("/health")
def health():
    checks = {}

    try:
        with get_db_connection() as connection:
            connection.execute("SELECT 1").fetchone()
        checks["postgres"] = {"status": "ok"}
    except psycopg.Error as error:
        checks["postgres"] = {
            "status": "error",
            "message": str(error).splitlines()[0],
        }

    try:
        redis_client.ping()
        checks["redis"] = {"status": "ok"}
    except redis.RedisError as error:
        checks["redis"] = {
            "status": "error",
            "message": str(error).splitlines()[0],
        }

    is_healthy = all(check["status"] == "ok" for check in checks.values())
    return jsonify(
        {
            "status": "ok" if is_healthy else "error",
            "checks": checks,
        }
    ), (200 if is_healthy else 503)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
