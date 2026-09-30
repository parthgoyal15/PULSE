"""SQLite persistence for demo state (transfers, stock, alerts). Not Firebase."""

from __future__ import annotations

import json
import os
import sqlite3
from typing import Any

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "pulse.db")


def _conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
    conn.commit()
    return conn


def save(key: str, value: Any) -> None:
    conn = _conn()
    conn.execute(
        "INSERT OR REPLACE INTO kv (k, v) VALUES (?, ?)",
        (key, json.dumps(value)),
    )
    conn.commit()
    conn.close()


def load(key: str, default: Any) -> Any:
    conn = _conn()
    row = conn.execute("SELECT v FROM kv WHERE k = ?", (key,)).fetchone()
    conn.close()
    if not row:
        return default
    try:
        return json.loads(row[0])
    except json.JSONDecodeError:
        return default
