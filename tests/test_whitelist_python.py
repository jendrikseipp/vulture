import subprocess
import sys

from .test_script import call_vulture, REPO

whitelist_file = 'whitelist_python.py'


def test_whitelist_python_with_python():
    assert subprocess.call(
        [sys.executable, whitelist_file], cwd=REPO) == 0


def test_whitelist_python_with_vulture():
    assert call_vulture([whitelist_file]) == 0
