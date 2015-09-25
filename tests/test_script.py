import os.path
import subprocess
import sys


DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(DIR)


def test_script():
    assert subprocess.call(
        [sys.executable, 'vulture.py', 'whitelist.py', 'vulture.py'],
        cwd=REPO) == 0


def test_exclude():
    assert subprocess.call(
        [sys.executable, 'vulture.py', '--exclude', 'vulture.py'],
        cwd=REPO) == 0


def test_missing_file():
    assert subprocess.call(
        [sys.executable, 'vulture.py', 'missing.py'], cwd=REPO) == 1
