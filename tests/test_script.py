import glob
import os.path
import subprocess
import sys

from . import call_vulture, REPO, WHITELISTS
from vulture.utils import ExitCode


def test_module_with_explicit_whitelists():
    assert call_vulture(["vulture/"] + WHITELISTS) == ExitCode.NoDeadCode


def test_module_with_implicit_whitelists():
    assert call_vulture(["vulture/"]) == ExitCode.NoDeadCode


def test_module_without_whitelists():
    assert (
        call_vulture(["vulture/", "--exclude", "whitelists"])
        == ExitCode.DeadCode
    )


def test_missing_file():
    assert call_vulture(["missing.py"]) == ExitCode.InvalidInput


def test_tests():
    assert call_vulture(["tests/"]) == ExitCode.NoDeadCode


def test_whitelists_with_python():
    for whitelist in WHITELISTS:
        assert (
            subprocess.call([sys.executable, whitelist], cwd=REPO)
            == ExitCode.NoDeadCode
        )


def test_pyc():
    assert call_vulture(["missing.pyc"]) == 1


def test_sort_by_size():
    assert (
        call_vulture(["vulture/utils.py", "--sort-by-size"])
        == ExitCode.DeadCode
    )


def test_min_confidence():
    assert (
        call_vulture(
            [
                "vulture/core.py",
                "--exclude",
                "whitelists",
                "--min-confidence",
                "100",
            ]
        )
        == ExitCode.NoDeadCode
    )


def test_exclude():
    def get_csv(paths):
        return ",".join(os.path.join("vulture", path) for path in paths)

    def call_vulture_with_excludes(excludes):
        return call_vulture(["vulture/", "--exclude", get_csv(excludes)])

    assert (
        call_vulture_with_excludes(["core.py", "utils.py"])
        == ExitCode.DeadCode
    )
    assert (
        call_vulture_with_excludes(glob.glob("vulture/*.py"))
        == ExitCode.NoDeadCode
    )


def test_make_whitelist():
    assert (
        call_vulture(
            ["vulture/", "--make-whitelist", "--exclude", "whitelists"]
        )
        == ExitCode.DeadCode
    )
    assert (
        call_vulture(["vulture/", "--make-whitelist"]) == ExitCode.NoDeadCode
    )


def test_version():
    assert call_vulture(["--version"]) == ExitCode.NoDeadCode
