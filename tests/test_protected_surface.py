"""Tests for protected competition mechanics enforcement."""

from pathlib import Path
import subprocess

import pytest

from amm_competition.competition.protected_surface import (
    OVERRIDE_ENV_VAR,
    ProtectedSurfaceChecker,
    ProtectedSurfaceError,
)


def _git(args: list[str], *, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def _build_protected_repo(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    protected_path = repo_root / "amm_competition" / "competition" / "config.py"
    protected_path.parent.mkdir(parents=True)
    (repo_root / ".competition-protected-paths").write_text(
        "amm_competition/competition/config.py\n"
    )
    protected_path.write_text("BASELINE = 1\n")

    _git(["git", "init"], cwd=repo_root)
    _git(["git", "config", "user.name", "Test User"], cwd=repo_root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=repo_root)
    _git(["git", "add", "."], cwd=repo_root)
    _git(["git", "commit", "-m", "init"], cwd=repo_root)
    return repo_root, protected_path


def test_protected_surface_blocks_dirty_changes(tmp_path):
    repo_root, protected_path = _build_protected_repo(tmp_path)
    protected_path.write_text("BASELINE = 2\n")

    checker = ProtectedSurfaceChecker(repo_root=repo_root)
    with pytest.raises(ProtectedSurfaceError, match="protected competition mechanics"):
        checker.ensure_runtime_eval_allowed()


def test_protected_surface_override_allows_dirty_changes(tmp_path):
    repo_root, protected_path = _build_protected_repo(tmp_path)
    protected_path.write_text("BASELINE = 2\n")

    checker = ProtectedSurfaceChecker(
        repo_root=repo_root,
        env={OVERRIDE_ENV_VAR: "1"},
    )
    checker.ensure_runtime_eval_allowed()


def test_protected_surface_rejects_fingerprint_mismatch(tmp_path):
    repo_root, protected_path = _build_protected_repo(tmp_path)
    checker = ProtectedSurfaceChecker(repo_root=repo_root)
    recorded = checker.current_fingerprint().to_payload()

    protected_path.write_text("BASELINE = 2\n")
    with pytest.raises(ProtectedSurfaceError, match="different protected competition mechanics surface"):
        checker.verify_recorded_fingerprint(recorded, run_id="mar26")
