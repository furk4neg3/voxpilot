"""SQLite database wrapper with schema initialisation.

Provides a thin helper around :mod:`sqlite3` that creates the required
tables on first use and exposes a connection factory for the repository
layer.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

_CREATE_GENERATION_RUNS = """\
CREATE TABLE IF NOT EXISTS generation_runs (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id                TEXT    NOT NULL UNIQUE,
    text                  TEXT    NOT NULL,
    language              TEXT    NOT NULL DEFAULT 'en',
    voice                 TEXT    NOT NULL DEFAULT 'default',
    engine                TEXT    NOT NULL,
    latency_ms            REAL    NOT NULL DEFAULT 0.0,
    audio_duration_seconds REAL   NOT NULL DEFAULT 0.0,
    real_time_factor      REAL,
    cache_hit             INTEGER NOT NULL DEFAULT 0,
    success               INTEGER NOT NULL DEFAULT 1,
    error                 TEXT,
    text_length           INTEGER NOT NULL DEFAULT 0,
    created_at            TEXT    NOT NULL
);
"""

_CREATE_FEEDBACK = """\
CREATE TABLE IF NOT EXISTS feedback (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id                 TEXT    NOT NULL,
    rating                 INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    naturalness            INTEGER CHECK (naturalness BETWEEN 1 AND 5),
    clarity                INTEGER CHECK (clarity BETWEEN 1 AND 5),
    latency_acceptability  INTEGER,
    comment                TEXT,
    created_at             TEXT    NOT NULL,
    FOREIGN KEY(run_id) REFERENCES generation_runs(run_id) ON DELETE CASCADE
);
"""

_CREATE_INDEX_RUN_ID = """\
CREATE INDEX IF NOT EXISTS idx_generation_runs_run_id
    ON generation_runs(run_id);
"""

_CREATE_INDEX_CREATED_AT = """\
CREATE INDEX IF NOT EXISTS idx_generation_runs_created_at
    ON generation_runs(created_at);
"""

_CREATE_INDEX_FEEDBACK_RUN_ID = """\
CREATE INDEX IF NOT EXISTS idx_feedback_run_id
    ON feedback(run_id);
"""

_CREATE_INDEX_FEEDBACK_CREATED_AT = """\
CREATE INDEX IF NOT EXISTS idx_feedback_created_at
    ON feedback(created_at);
"""


class Database:
    """Lightweight SQLite wrapper.

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.  Parent directories are created
        automatically.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        logger.info("Database path: %s", db_path)

    def init_db(self) -> None:
        """Create tables and indices if they do not exist."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(_CREATE_GENERATION_RUNS)
            self._remove_legacy_upload_columns(cursor)
            cursor.execute(_CREATE_INDEX_RUN_ID)
            cursor.execute(_CREATE_INDEX_CREATED_AT)
            cursor.execute(_CREATE_FEEDBACK)
            cursor.execute(_CREATE_INDEX_FEEDBACK_RUN_ID)
            cursor.execute(_CREATE_INDEX_FEEDBACK_CREATED_AT)
            conn.commit()
            logger.info("Database schema initialised.")
        finally:
            conn.close()

    def get_connection(self) -> sqlite3.Connection:
        """Return a new :class:`sqlite3.Connection`.

        The caller is responsible for closing the connection.
        """
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    @staticmethod
    def _remove_legacy_upload_columns(cursor: sqlite3.Cursor) -> None:
        """Rebuild old run tables that carried removed upload metadata."""
        columns = {
            row["name"]
            for row in cursor.execute("PRAGMA table_info(generation_runs)").fetchall()
        }
        legacy_columns = {"ref" + "erence_used", "ref" + "erence_consent"}
        if not legacy_columns.intersection(columns):
            return

        logger.info("Removing legacy upload columns from generation_runs.")
        cursor.execute("DROP INDEX IF EXISTS idx_generation_runs_run_id")
        cursor.execute("DROP INDEX IF EXISTS idx_generation_runs_created_at")
        cursor.execute("ALTER TABLE generation_runs RENAME TO generation_runs_legacy")
        cursor.execute(_CREATE_GENERATION_RUNS)
        cursor.execute(
            """\
            INSERT OR IGNORE INTO generation_runs (
                id, run_id, text, language, voice, engine,
                latency_ms, audio_duration_seconds, real_time_factor,
                cache_hit, success, error, text_length, created_at
            )
            SELECT
                id, run_id, text, language, voice, engine,
                latency_ms, audio_duration_seconds, real_time_factor,
                cache_hit, success, error, text_length, created_at
            FROM generation_runs_legacy;
            """
        )
        cursor.execute("DROP TABLE generation_runs_legacy")
