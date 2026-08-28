"""Baseline — single LLM prompt with README + file tree, no tools."""

from __future__ import annotations

import json
import os
from pathlib import Path


def run_baseline(url: str, repo_path: Path) -> dict[str, object]:
    """
    Fair baseline: one LLM call with README + tree. For MVP without LLM key, fallback to heuristic.
    Returns {"overall": int, "areas": [...]}
    """
    # Collect README + file tree (no sandbox execution)
    readme = ""
    for name in ["README.md", "readme.md"]:
        p = repo_path / name
        if p.exists():
            readme = p.read_text(encoding="utf-8", errors="ignore")[:2000]
            break
    # File tree (top 30)
    files = [str(p.relative_to(repo_path)) for p in repo_path.rglob("*") if p.is_file()][:30]
    tree = "\n".join(files)

    # If OPENAI key, call LLM, else heuristic 60
    key = os.getenv("OPENAI_API_KEY", "")
    if key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=key)
            prompt = f"You are a diligence reviewer. Score this repo 0-100 overall given README and file tree. README:\n{readme[:1500]}\nTree:\n{tree[:1500]}\nReturn JSON {{\"overall\": int, \"reason\": str}} only."
            resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0)
            content = resp.choices[0].message.content or "{}"
            # try parse
            j = json.loads(content[content.find("{") : content.rfind("}") + 1])
            return {"overall": int(j.get("overall", 60)), "reason": j.get("reason", ""), "method": "llm"}
        except Exception as e:
            return {"overall": 60, "reason": f"llm fail {e}", "method": "heuristic"}

    # Heuristic: longer README = higher score (biased, exactly what baseline does wrong)
    score = 60 + min(20, len(readme) // 200) - min(10, len(files) // 10)
    return {"overall": max(20, min(95, score)), "reason": "heuristic baseline", "method": "heuristic"}
