import os.path
import subprocess
import sys

from .test_script import call_vulture, REPO


def test_whitelist_python_with_python():
    assert subprocess.call(
        [sys.executable, 'whitelist_python.py'], cwd=REPO) == 0


def test_whitelist_python_with_vulture():
    """
    Run vulture over an example file (tests/example.py) containing
    keywords for testing whitelist_python and check output.
    """
    whitelist_file = 'whitelist_python.py'
    assert call_vulture([whitelist_file, 'whitelist_python.py']) == 0
    assert call_vulture([whitelist_file]) == 0
