import os.path
import subprocess
import sys


DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(DIR)


def test_script():
    assert subprocess.call(
        [sys.executable, 'vulture.py', 'whitelist.py', 'vulture.py'],
        cwd=REPO) == 0
