from pathlib import Path

from codecat.agents.aggregator import aggregate, overall_score, verdict_for
from codecat.agents.build_agent import BuildResult
from codecat.agents.depsec_agent import DepSecResult
from codecat.agents.fix_planner import plan_fix
from codecat.agents.static_claim_agent import ClaimCheck, StaticClaimResult
from codecat.tools.sandbox import SandboxResult


def _build(pass_val: bool | None) -> BuildResult:
    return BuildResult(
        install_pass=True,
        test_pass=pass_val,
        docker_pass=None,
        install_log=None,
        test_log=SandboxResult("test", 0 if pass_val else 1, "ok" if pass_val else "fail", "", False),
        docker_log=None,
        test_summary="ok" if pass_val else "fail",
        package_manager="npm",
    )


def _depsec(high: int) -> DepSecResult:
    return DepSecResult(
        npm_audit_log=None,
        pip_audit_log=None,
        npm_parsed={},
        pip_parsed=[],
        high_cves=high,
        bus_factor=2,
        has_docker=False,
        git_log=SandboxResult("git log", 0, "", "", False),
    )


def _static(has_circular: bool, claims: list[ClaimCheck] | None = None) -> StaticClaimResult:
    return StaticClaimResult(
        circular_log=SandboxResult("madge", 0, "circular" if has_circular else "", "", False),
        complexity_log=SandboxResult("radon", 0, "", "", False),
        cloc_log=SandboxResult("cloc", 0, "", "", False),
        claims=claims or [],
        has_circular=has_circular,
    )


def test_aggregate_testing_pass() -> None:
    areas = aggregate("https://example.com", _build(True), _depsec(0), _static(False))
    testing = [a for a in areas if a.area == "Testing"][0]
    assert testing.score == 90
    assert testing.evidence[0].file == "evidence/test.log"


def test_aggregate_testing_fail_and_cve() -> None:
    areas = aggregate("https://example.com", _build(False), _depsec(3), _static(True))
    scores = {a.area: a.score for a in areas}
    assert scores["Testing"] == 35
    assert scores["Dependencies"] == 30
    assert scores["Architecture"] == 45


def test_aggregate_claim_fail() -> None:
    claims = [ClaimCheck(text="npm test passes", verdict="FAIL", evidence_ref="test.log:1")]
    areas = aggregate("https://example.com", _build(False), _depsec(0), _static(False, claims))
    assert any(a.area == "README claims" for a in areas)


def test_overall_and_verdict() -> None:
    areas = aggregate("https://example.com", _build(True), _depsec(0), _static(False))
    score = overall_score(areas)
    assert 0 <= score <= 100
    assert verdict_for(90) == "BUY"
    assert verdict_for(60) == "HOLD"
    assert verdict_for(30) == "REJECT"


def test_plan_fix_tests() -> None:
    # tests fail takes priority
    target = plan_fix(False, 5, False, Path("/tmp"))
    assert target is not None and target.kind == "tests"


def test_plan_fix_dep_bump(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"dependencies":{"lodash":"4.17.19"}}', encoding="utf-8")
    target = plan_fix(True, 1, False, tmp_path)
    assert target is not None and target.kind == "dep_bump"


def test_plan_fix_none(tmp_path: Path) -> None:
    target = plan_fix(True, 0, False, tmp_path)
    assert target is None
