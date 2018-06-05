import subprocess
import sys

from . import REPO, WHITELISTS


def call_vulture(args, **kwargs):
    return subprocess.call(
        [sys.executable, '-m', 'vulture'] + args, cwd=REPO, **kwargs)


def test_module_with_explicit_whitelists():
    assert call_vulture(['vulture/'] + WHITELISTS) == 0


def test_module_with_implicit_whitelists():
    assert call_vulture(['vulture/']) == 0


def test_module_without_whitelists():
    assert call_vulture(['vulture/', '--exclude', 'whitelists']) == 1


def test_missing_file():
    assert call_vulture(['missing.py']) == 1


def test_tests():
    assert call_vulture(['tests/']) == 0


def test_whitelists_with_python():
    for whitelist in WHITELISTS:
        assert subprocess.call([sys.executable, whitelist], cwd=REPO) == 0


def test_pyc():
    assert call_vulture(['missing.pyc']) == 1


def test_sort_by_size():
    assert call_vulture(['vulture/utils.py', '--sort-by-size']) == 1


def test_min_confidence():
    assert call_vulture([
        'vulture/core.py', '--exclude', 'whitelists',
        '--min-confidence', '100']) == 0
