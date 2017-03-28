import os.path
from subprocess import call, Popen, PIPE
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(DIR)


def test_whitelist_python():
    assert call(
        [sys.executable, 'whitelist_python.py'], cwd=REPO) == 0


def test_whitelist_python_function():
    """
    Run vulture over an example file (tests/example.py) containing
    keywords for testing whitelist_python and check output.
    """
    example_file = 'tests/example.txt'
    p = Popen([sys.executable, example_file, 'whitelist_python.py'],
              stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")
    if err.decode("utf-8").find("could not be found.") != -1:
        raise IOError("%s file wasn't found" % example_file)
    assert err == b''
    assert output == b''
