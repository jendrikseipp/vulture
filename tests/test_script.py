import glob
import os.path
import subprocess
import sys

import pytest

from vulture.utils import ExitCode

from . import REPO, WHITELISTS, call_vulture, v

assert v  # Silence pyflakes.


def test_module_with_explicit_whitelists():
    assert call_vulture(["vulture/", *WHITELISTS]) == ExitCode.NoDeadCode


def test_module_with_implicit_whitelists():
    assert call_vulture(["vulture/"]) == ExitCode.NoDeadCode


def test_module_without_whitelists():
    assert (
        call_vulture(["vulture/", "--exclude", "whitelists"])
        == ExitCode.DeadCode
    )


def test_missing_file():
    assert call_vulture(["missing.py"]) == ExitCode.InvalidInput


@pytest.mark.parametrize(
    "option", ["paths", "exclude", "ignore_decorators", "ignore_names"]
)
def test_config_rejects_non_string_list_items(option, tmp_path, capfd):
    config = tmp_path / "pyproject.toml"
    settings = f'[tool.vulture]\n{option} = ["vulture", 42]\n'
    if option != "paths":
        settings += 'paths = ["vulture"]\n'
    config.write_text(settings, encoding="utf-8")

    status = call_vulture([f"--config={config}"])
    out, err = capfd.readouterr()

    assert status == ExitCode.InvalidCmdlineArguments
    assert not out
    assert err == f"Data type for {option} must be a list of strings\n"


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


def test_exclude_empty_pattern(v, tmp_path):
    """An empty exclude pattern must not exclude everything."""
    module = tmp_path / "module.py"
    module.write_text("import os\n")
    v.scavenge([module], exclude=["", "no_match"])
    assert [item.name for item in v.get_unused_code()] == ["os"]
