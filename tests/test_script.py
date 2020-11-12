import glob
import os
import subprocess
import sys
from pathlib import Path

from . import call_vulture, run_vulture, REPO, WHITELISTS


def test_module_with_explicit_whitelists():
    assert call_vulture(["vulture/"] + WHITELISTS) == 0


def test_module_with_implicit_whitelists():
    assert call_vulture(["vulture/"]) == 0


def test_module_without_whitelists():
    assert call_vulture(["vulture/", "--exclude", "whitelists"]) == 1


def test_missing_file():
    assert call_vulture(["missing.py"]) == 1


def test_tests():
    assert call_vulture(["tests/"]) == 0


def test_whitelists_with_python():
    for whitelist in WHITELISTS:
        assert subprocess.call([sys.executable, whitelist], cwd=REPO) == 0


def test_pyc():
    assert call_vulture(["missing.pyc"]) == 1


def test_sort_by_size():
    assert call_vulture(["vulture/utils.py", "--sort-by-size"]) == 1


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
        == 0
    )


def test_exclude():
    def get_csv(paths):
        return ",".join(os.path.join("vulture", path) for path in paths)

    def call_vulture_with_excludes(excludes):
        return call_vulture(["vulture/", "--exclude", get_csv(excludes)])

    assert call_vulture_with_excludes(["core.py", "utils.py"]) == 1
    assert call_vulture_with_excludes(glob.glob("vulture/*.py")) == 0


def test_make_whitelist():
    assert (
        call_vulture(
            ["vulture/", "--make-whitelist", "--exclude", "whitelists"]
        )
        == 1
    )
    assert call_vulture(["vulture/", "--make-whitelist"]) == 0


def test_absolute_paths():
    try:
        completed_process = run_vulture(
            ["--format", "absolute", "deadcode/"], check=False
        )
        output_lines = completed_process.stdout.strip().split(os.linesep)
        for line in output_lines:
            if line:
                lineparts = line.split(":")
                # platform independent logic
                # Windows differs from other root paths, uses ':' in volumes
                # unix-like platforms should have 3 parts on an output line
                # windows (absolute paths) have > 3 (4) including drive spec
                partcount = len(lineparts)
                filename = lineparts[0]
                if partcount >= 3:
                    for i in range(1, partcount - 2):
                        filename += f":{lineparts[i]}"
                # make sure the file resolves to an actual file
                # and it's an absolute path
                path = Path(filename)
                assert path.exists()
                path = path.resolve()
                assert path.is_absolute()
    except subprocess.TimeoutExpired as time_err:
        raise AssertionError from time_err
    except subprocess.SubprocessError as sub_err:
        raise AssertionError from sub_err


def test_path_format_config():
    """
    Verify any unrecognized format generates an error.
    By definition, implemented format names will be registered,
    so no sense testing them.
    """
    assert call_vulture(["--format", "unimplemented", "tests/"]) == 1
