import os.path
import sys
import subprocess

from .test_script import call_vulture, REPO


def test_whitelist_python():
    assert subprocess.call(
        [sys.executable, 'whitelist_python.py'], cwd=REPO) == 0


def test_whitelist_python_function():
    """
    Run vulture over an example file (tests/example.py) containing
    keywords for testing whitelist_python and check output.
    """
    example_file = os.path.join(REPO, 'tests/example_whitelist_python.txt')
    assert call_vulture([example_file, 'whitelist_python.py']) == 0
    assert call_vulture([example_file]) == 1
