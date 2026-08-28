"""Strict Pydantic schemas — every report row must have evidence."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class Severity(StrEnum):
    critical = "critical"
    medium = "medium"
    low = "low"


class Evidence(BaseModel):
    """Single evidence link — file:line or log:line."""

    file: str = Field(description="evidence/<file>")
    line: int | None = Field(default=None, description="1-indexed line number")
    excerpt: str = Field(default="", max_length=500)

    def ref(self) -> str:
        return f"{self.file}:{self.line}" if self.line is not None else self.file


class RiskArea(BaseModel):
    """One row in the evidence table."""

    area: Literal["Testing", "Dependencies", "Security", "Architecture", "Maintainability", "README claims"]
    score: int = Field(ge=0, le=100)
    severity: Severity
    evidence: list[Evidence] = Field(min_length=1, description="At least one evidence per row — verified")
    cost_to_fix: str = Field(default="", description="e.g. '2h' or '0.5 sprint'")
    summary: str = Field(max_length=300)


class RiskReport(BaseModel):
    """Final memo — validated, evidence-backed."""

    repo_url: str
    repo_hash: str
    overall_before: int = Field(ge=0, le=100)
    overall_after: int | None = Field(default=None, ge=0, le=100)
    verdict: Literal["BUY", "HOLD", "REJECT"]
    areas: list[RiskArea] = Field(min_length=3)
    patch_diff: str | None = Field(default=None, description="git diff or null")
    before_log_excerpt: str = Field(default="")
    after_log_excerpt: str | None = Field(default=None)
    reproduction_commands: list[str] = Field(default_factory=list)
