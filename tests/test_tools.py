from pathlib import Path

from codecat.tools.audit_tools import count_high_cves
from codecat.tools.git_tools import bus_factor_from_shortlog
from codecat.tools.sandbox import SandboxResult, repo_hash, run_in_sandbox
from codecat.tools.static_tools import claim_verdict, extract_readme_claims


def test_repo_hash_deterministic() -> None:
    assert repo_hash("https://github.com/pallets/flask") == repo_hash("https://github.com/pallets/flask")
    assert len(repo_hash("x")) == 12


def test_sandbox_run_echo(tmp_path: Path) -> None:
    result = run_in_sandbox("echo hello", cwd=tmp_path, timeout_sec=5)
    assert result.returncode == 0
    assert "hello" in result.stdout
    assert isinstance(result, SandboxResult)


def test_bus_factor() -> None:
    log = "   80\tAlice\n   10\tBob\n   10\tCarol\n"
    assert bus_factor_from_shortlog(log) == 1  # only Alice >10%
    log2 = "  50\tAlice\n  50\tBob\n"
    assert bus_factor_from_shortlog(log2) == 2
    assert bus_factor_from_shortlog("") == 0


def test_count_high_cves_npm() -> None:
    parsed = {"vulnerabilities": {"lodash": {"severity": "high"}, "other": {"severity": "low"}}}
    assert count_high_cves(parsed) == 1
    assert count_high_cves([]) == 0


def test_claim_verdict() -> None:
    v, _ = claim_verdict("npm test passes", test_pass=False, docker_pass=None, install_pass=None)
    assert v == "FAIL"
    v2, _ = claim_verdict("docker build works", test_pass=None, docker_pass=True, install_pass=None)
    assert v2 == "PASS"


def test_extract_claims(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("This project has npm test passes easily\nand docker build works", encoding="utf-8")
    claims = extract_readme_claims(tmp_path)
    assert len(claims) >= 1
