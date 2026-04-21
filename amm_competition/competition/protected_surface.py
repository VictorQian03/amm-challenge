"""Shared enforcement for protected competition mechanics."""

from __future__ import annotations

from dataclasses import dataclass
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Mapping, cast

OVERRIDE_ENV_VAR = "ALLOW_COMPETITION_MECHANICS_EDIT"
PROTECTED_MANIFEST = ".competition-protected-paths"


class ProtectedSurfaceError(RuntimeError):
    """Raised when the protected competition mechanics surface is unsafe."""


@dataclass(frozen=True)
class ProtectedSurfaceFingerprint:
    """Stable summary of the protected mechanics surface for one repo state."""

    manifest_path: str
    sha256: str
    file_count: int

    def to_payload(self) -> dict[str, str | int]:
        return {
            "manifest_path": self.manifest_path,
            "sha256": self.sha256,
            "file_count": self.file_count,
        }


@dataclass(frozen=True)
class ProtectedSurfaceChanges:
    """Protected working tree changes grouped by git state."""

    staged: tuple[str, ...]
    unstaged: tuple[str, ...]
    untracked: tuple[str, ...]

    @property
    def all_paths(self) -> tuple[str, ...]:
        return tuple(sorted({*self.staged, *self.unstaged, *self.untracked}))


class ProtectedSurfaceChecker:
    """Read the protected-path manifest and enforce the freeze contract."""

    def __init__(
        self,
        *,
        repo_root: Path | str,
        env: Mapping[str, str] | None = None,
        manifest_name: str = PROTECTED_MANIFEST,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.env = os.environ if env is None else env
        self.manifest_path = self.repo_root / manifest_name
        self._manifest_relpath = self.manifest_path.relative_to(self.repo_root).as_posix()

    @classmethod
    def discover(
        cls,
        *,
        cwd: Path | str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> "ProtectedSurfaceChecker":
        root = cls._git_output(
            ["rev-parse", "--show-toplevel"],
            cwd=Path.cwd() if cwd is None else Path(cwd),
        ).strip()
        return cls(repo_root=root, env=env)

    def current_fingerprint(self) -> ProtectedSurfaceFingerprint:
        entries: list[dict[str, str]] = []
        for relpath in self._protected_file_relpaths():
            path = self.repo_root / relpath
            entries.append(
                {
                    "path": relpath,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )

        digest = hashlib.sha256(
            json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return ProtectedSurfaceFingerprint(
            manifest_path=self._manifest_relpath,
            sha256=digest,
            file_count=len(entries),
        )

    def ensure_runtime_eval_allowed(self) -> None:
        if self._override_enabled():
            return
        changes = self.dirty_changes()
        if not changes.all_paths:
            return
        raise ProtectedSurfaceError(self._dirty_tree_message("hill-climb eval", changes))

    def dirty_changes(self) -> ProtectedSurfaceChanges:
        return ProtectedSurfaceChanges(
            staged=self._filter_protected_paths(
                self._git_name_only(["diff", "--cached", "--name-only", "--diff-filter=ACMRD"])
            ),
            unstaged=self._filter_protected_paths(
                self._git_name_only(["diff", "--name-only", "--diff-filter=ACMRD"])
            ),
            untracked=self._filter_protected_paths(
                self._git_name_only(["ls-files", "--others", "--exclude-standard"])
            ),
        )

    def hook_check(self, *, mode: str) -> None:
        if self._override_enabled():
            return
        changes = self.dirty_changes()
        if not changes.all_paths:
            return
        raise ProtectedSurfaceError(self._dirty_tree_message(mode, changes))

    def verify_recorded_fingerprint(
        self,
        recorded_payload: object,
        *,
        run_id: str,
    ) -> None:
        if not isinstance(recorded_payload, dict):
            raise ProtectedSurfaceError(
                f"Run '{run_id}' does not record a valid protected_surface_fingerprint. "
                "Start a fresh run_id under the current evaluator."
            )
        recorded_payload_dict = cast(dict[str, object], recorded_payload)
        current = self.current_fingerprint().to_payload()
        if recorded_payload_dict == current:
            return

        details = [
            f"Run '{run_id}' is pinned to a different protected competition mechanics surface.",
            f"Recorded fingerprint: {recorded_payload_dict.get('sha256')}",
            f"Current fingerprint: {current['sha256']}",
        ]
        changes = self.dirty_changes()
        if changes.all_paths:
            details.append("Current protected working tree changes:")
            details.extend(f"  - {path}" for path in changes.all_paths)
        details.append(
            "Start a fresh run_id before continuing under the new evaluator surface."
        )
        raise ProtectedSurfaceError("\n".join(details))

    def _override_enabled(self) -> bool:
        return self.env.get(OVERRIDE_ENV_VAR) == "1"

    def _protected_patterns(self) -> tuple[str, ...]:
        if not self.manifest_path.exists():
            raise ProtectedSurfaceError(
                f"Protected mechanics manifest missing: {self.manifest_path}"
            )
        patterns: list[str] = []
        for raw_line in self.manifest_path.read_text().splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if line:
                patterns.append(line)
        return tuple(patterns)

    def _protected_file_relpaths(self) -> tuple[str, ...]:
        relpaths = {self._manifest_relpath}
        for pattern in self._protected_patterns():
            for path in self.repo_root.glob(pattern):
                if path.is_file():
                    relpaths.add(path.relative_to(self.repo_root).as_posix())
        return tuple(sorted(relpaths))

    def _filter_protected_paths(self, paths: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(path for path in paths if self._is_protected_path(path)))

    def _is_protected_path(self, relpath: str) -> bool:
        if relpath == self._manifest_relpath:
            return True
        return any(
            fnmatch.fnmatchcase(relpath, pattern)
            for pattern in self._protected_patterns()
        )

    def _git_name_only(self, args: list[str]) -> tuple[str, ...]:
        output = self._git_output(args, cwd=self.repo_root)
        return tuple(sorted(line.strip() for line in output.splitlines() if line.strip()))

    def _dirty_tree_message(self, mode: str, changes: ProtectedSurfaceChanges) -> str:
        lines = [
            f"Blocked {mode}: working tree changes touch protected competition mechanics.",
            "",
            "Protected paths:",
        ]
        lines.extend(f"  - {path}" for path in changes.all_paths)
        lines.extend(
            [
                "",
                f"If this evaluator edit is intentional, rerun with {OVERRIDE_ENV_VAR}=1.",
                "Do not continue an existing retained run after changing the evaluator; "
                "start a fresh run_id instead.",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _git_output(args: list[str], *, cwd: Path) -> str:
        process = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if process.returncode != 0:
            raise ProtectedSurfaceError(
                process.stderr.strip() or process.stdout.strip() or "git failed"
            )
        return process.stdout


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Protect competition mechanics from accidental edits"
    )
    parser.add_argument(
        "--mode",
        required=True,
        help="Hook or command mode label used in failure messages",
    )
    args = parser.parse_args()

    try:
        ProtectedSurfaceChecker.discover().hook_check(mode=args.mode)
    except ProtectedSurfaceError as exc:
        print(exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
