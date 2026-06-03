"""High-resolution timing utilities."""

from __future__ import annotations

import time


class Timer:
    """Context manager that tracks wall-clock elapsed time in milliseconds.

    Usage::

        with Timer() as t:
            do_expensive_work()
        print(f"Took {t.elapsed_ms:.1f} ms")
    """

    def __init__(self) -> None:
        self._start: float = 0.0
        self._end: float = 0.0

    # ── Context-manager protocol ──────────────────────────────────────

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        self._end = time.perf_counter()

    # ── Convenience ───────────────────────────────────────────────────

    @property
    def elapsed_ms(self) -> float:
        """Elapsed time in milliseconds, including while the timer is active."""
        if self._start <= 0:
            return 0.0
        end = self._end if self._end > 0 else time.perf_counter()
        return (end - self._start) * 1000.0

    @property
    def elapsed_seconds(self) -> float:
        """Elapsed time in seconds (computed from ``elapsed_ms``)."""
        return self.elapsed_ms / 1000.0
