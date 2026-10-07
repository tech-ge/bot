"""Validate generated text/media before publishing."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from loguru import logger

from config.settings import settings
from copyright_guard.similarity import max_similarity


@dataclass
class OutputCheckResult:
    ok: bool
    max_similarity: float = 0.0
    reason: str = ""
    flags: list[str] = field(default_factory=list)


class OutputChecker:
    def __init__(self, corpus: Iterable[str] | None = None) -> None:
        self.threshold = float(
            settings.copyright_guard.get("min_similarity_flag", 0.85)
        )
        self.corpus: list[str] = list(corpus or [])
        self.report_dir = settings.base_dir / "copyright_guard" / "reports"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.report_dir / "flagged_content.log"

    def check(self, text: str) -> OutputCheckResult:
        if not text.strip():
            return OutputCheckResult(False, reason="empty_output")
        score = max_similarity(text, self.corpus) if self.corpus else 0.0
        if score >= self.threshold:
            self._log_flag(text, score, "high_similarity")
            return OutputCheckResult(
                False, score,
                reason="high_similarity",
                flags=[f"similarity={score:.3f}"],
            )
        return OutputCheckResult(True, score)

    def _log_flag(self, text: str, score: float, reason: str) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "similarity": score,
            "excerpt": text[:280],
        }
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        logger.warning("Copyright flag: {r} sim={s:.3f}", r=reason, s=score)

    def add_corpus(self, texts: Iterable[str]) -> None:
        self.corpus.extend(texts)
