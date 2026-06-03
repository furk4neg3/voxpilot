"""Structured JSON logging configuration.

Call ``setup_logging(level)`` once at application startup to wire up a
JSON-formatted root logger suitable for 12-factor cloud deployments.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone


class _JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Attach exception info when present.
        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Forward any extra keys injected via ``logging.info("…", extra={…})``.
        for key in ("run_id", "engine", "latency_ms", "cache_hit", "voice"):
            value = getattr(record, key, None)
            if value is not None:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger with a JSON formatter on *stderr*.

    Parameters
    ----------
    level:
        Standard Python log-level name (``DEBUG``, ``INFO``, ``WARNING``, …).
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_JSONFormatter())

    root = logging.getLogger()
    # Remove any handlers that may have been added by third-party libs.
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(numeric_level)

    # Silence overly chatty third-party loggers.
    for noisy in ("urllib3", "httpcore", "httpx", "transformers", "datasets"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
