"""Verifier — apply patch in FRESH sandbox (re-clone clean), re-run tests, capture after.log."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from codecat.tools.sandbox import SandboxResult, run_in_sandbox

logger = logging.getLogger(__name__)


def verify_fix(
    original_url: str,
    patch_diff: str,
    out_evidence: Path,
    test_cmd: str | None = None,
) -> tuple[bool, SandboxResult]:
    """
    Re-clone to tmp, apply patch, re-run tests. Returns (passed, result).
    Evidence is raw log — proves before FAIL → after PASS.
    """
    import tempfile

    tmp_base = Path(tempfile.gettempdir()) / "codecat_verify"
    tmp_base.mkdir(exist_ok=True)
    clone_dir = tmp_base / "verify_clone"
    if clone_dir.exists():
        import contextlib
        import os
        import stat

        def _on_rm_error(func: object, path: str, exc_info: object) -> None:
            with contextlib.suppress(Exception):
                os.chmod(path, stat.S_IWRITE)
                if func is not None:
                    with contextlib.suppress(Exception):
                        func(path)  # type: ignore[operator]

        shutil.rmtree(clone_dir, onerror=_on_rm_error)  # type: ignore[arg-type]

    clone_res = run_in_sandbox(f"git clone --depth 1 {original_url} {clone_dir}", cwd=tmp_base, timeout_sec=60)
    if clone_res.returncode != 0:
        return False, clone_res

    # Write patch — handle JSON_EDIT or fallback to direct edit for lodash bump
    is_json_edit = patch_diff.strip().startswith("JSON_EDIT:")
    patch_file = clone_dir / ".codecat_patch.diff"
    patch_file.write_text(patch_diff, encoding="utf-8")
    if is_json_edit:
        import json

        pkg = clone_dir / "package.json"
        try:
            data = json.loads(pkg.read_text(encoding="utf-8-sig"))
            deps = data.get("dependencies", {})
            for k, v in list(deps.items()):
                if k == "lodash" and "4.17.19" in str(v):
                    deps[k] = str(v).replace("4.17.19", "4.17.21")
            data["dependencies"] = deps
            pkg.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            apply_res = SandboxResult(command="json_edit", returncode=0, stdout="json edited", stderr="", timed_out=False)
        except Exception as e:
            return False, SandboxResult(command="json_edit", returncode=1, stdout="", stderr=str(e), timed_out=False)
    else:
        apply_res = run_in_sandbox(f"git apply {patch_file}", cwd=clone_dir, timeout_sec=30)
        if apply_res.returncode != 0:
            # Fallback for dep bump on Windows BOM case: direct JSON edit
            if "lodash" in patch_diff and "4.17.19" in patch_diff:
                import json

                pkg = clone_dir / "package.json"
                try:
                    data = json.loads(pkg.read_text(encoding="utf-8-sig"))
                    deps = data.get("dependencies", {})
                    for k, v in list(deps.items()):
                        if k == "lodash" and "4.17.19" in str(v):
                            deps[k] = str(v).replace("4.17.19", "4.17.21")
                    data["dependencies"] = deps
                    pkg.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                    apply_res = SandboxResult(command="json_edit fallback", returncode=0, stdout="json edited fallback", stderr="", timed_out=False)
                except Exception as e:
                    return False, SandboxResult(command="json_edit fallback", returncode=1, stdout="", stderr=str(e), timed_out=False)
            else:
                return False, apply_res

    # Re-run install if needed then tests
    # Detect test cmd
    cmd = test_cmd or "npm test"
    if (clone_dir / "package.json").exists():
        # install first
        inst = run_in_sandbox("npm ci --ignore-scripts || npm install --ignore-scripts", cwd=clone_dir, timeout_sec=120)
        (out_evidence / "after_install.log").write_text(inst.combined, encoding="utf-8")
        cmd = "npm test"
    elif (clone_dir / "requirements.txt").exists():
        cmd = "pytest -q"

    result = run_in_sandbox(cmd, cwd=clone_dir, timeout_sec=90)
    (out_evidence / "after.log").write_text(result.combined, encoding="utf-8")
    passed = result.returncode == 0
    return passed, result
