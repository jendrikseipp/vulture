import glob
import os.path
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(DIR)
WHITELISTS = glob.glob(os.path.join(REPO, 'vulture', 'whitelists', '*.py'))


def call_vulture(args, **kwargs):
    core = 'vulture'
    if sys.version_info < (2, 7):
        core = 'vulture.core'
    return subprocess.call(
        [sys.executable, '-m', core] + args, cwd=REPO, **kwargs)


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
    assert call_vulture(['vulture/', '--sort-by-size']) == 0


def test_min_confidence():
    assert call_vulture([
        'vulture/core.py', '--exclude', 'whitelists',
        '--min-confidence', '100']) == 0
