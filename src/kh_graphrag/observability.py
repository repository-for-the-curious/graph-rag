"""log_metrics (5.12): optional Langfuse tracing.

Every question becomes one trace with one span per LangGraph node, and eval scores
are attached to the trace. With no Langfuse keys configured, a no-op tracer is used
and nothing leaves the machine.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator

from kh_graphrag.config import Settings

log = logging.getLogger(__name__)


class Trace:
    """No-op trace; LangfuseTrace overrides these methods."""

    id: str | None = None

    @contextmanager
    def span(self, name: str, input: Any = None) -> Iterator[dict]:
        yield {}

    def generation(self, name: str, model: str, input: Any, output: Any) -> None:
        pass

    def end(self, output: Any = None) -> None:
        pass

    def score(self, name: str, value: float, comment: str | None = None) -> None:
        pass


class Tracer:
    def trace(self, name: str, input: Any = None, metadata: dict | None = None) -> Trace:
        return Trace()

    def flush(self) -> None:
        pass


class LangfuseTrace(Trace):
    def __init__(self, handle):
        self._t = handle
        self.id = handle.id

    @contextmanager
    def span(self, name: str, input: Any = None) -> Iterator[dict]:
        span = self._t.span(name=name, input=input)
        out: dict = {}
        try:
            yield out
        except Exception as exc:
            span.end(level="ERROR", status_message=str(exc))
            raise
        span.end(output=out or None)

    def generation(self, name: str, model: str, input: Any, output: Any) -> None:
        self._t.generation(name=name, model=model, input=input, output=output).end()

    def end(self, output: Any = None) -> None:
        self._t.update(output=output)

    def score(self, name: str, value: float, comment: str | None = None) -> None:
        self._t.score(name=name, value=float(value), comment=comment)


class LangfuseTracer(Tracer):
    def __init__(self, settings: Settings):
        from langfuse import Langfuse

        self._lf = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )

    def trace(self, name: str, input: Any = None, metadata: dict | None = None) -> Trace:
        return LangfuseTrace(self._lf.trace(name=name, input=input, metadata=metadata))

    def flush(self) -> None:
        self._lf.flush()


def make_tracer(settings: Settings) -> Tracer:
    if not settings.tracing_enabled:
        return Tracer()
    try:
        return LangfuseTracer(settings)
    except ImportError:
        log.warning("langfuse is not installed (pip install .[obs]); tracing disabled")
        return Tracer()


def log_metrics(trace: Trace, scores: dict[str, float | None]) -> None:
    for name, value in scores.items():
        if value is not None:
            trace.score(name, value)
