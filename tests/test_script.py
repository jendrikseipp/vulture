import os.path
import subprocess
import sys


DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(DIR)


def call_vulture(args, **kwargs):
    return subprocess.call(
        [sys.executable, 'vulture.py'] + args, cwd=REPO, **kwargs)


def test_script():
    assert call_vulture(['whitelist.py', 'vulture.py']) == 0


def test_exclude():
    assert call_vulture(['vulture.py', '--exclude', 'vulture.py']) == 0


def test_missing_file():
    assert call_vulture(['missing.py']) == 1


def test_dir():
    assert call_vulture(['tests']) == 0


def test_report():
    assert call_vulture(['vulture.py']) == 1


def test_whitelist():
    assert subprocess.call(
        [sys.executable, 'whitelist.py'], cwd=REPO) == 0


def test_pyc():
    assert call_vulture(['missing.pyc']) == 1
