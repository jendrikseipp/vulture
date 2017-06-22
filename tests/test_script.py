import os.path
import subprocess
import sys

from vulture import __version__

DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(DIR)
WHITELIST = os.path.join(REPO, 'vulture', 'whitelists', 'stdlib.py')


def call_vulture(args, **kwargs):
    return subprocess.call(
        [sys.executable, 'vulture/core.py'] + args, cwd=REPO, **kwargs)


def get_output(args):
    child = subprocess.Popen([sys.executable, "vulture/core.py"] + args,
                             cwd=REPO, stdout=subprocess.PIPE)
    return child.communicate()[0].decode("utf-8")


def test_script_with_explicit_whitelist():
    assert call_vulture(['vulture/core.py', WHITELIST]) == 0


def test_script_with_implicit_whitelist():
    assert call_vulture(['vulture/core.py']) == 0


def test_script_without_whitelist():
    assert call_vulture(['vulture/core.py', '--exclude', 'whitelists']) == 1


def test_exclude():
    assert call_vulture(['vulture/core.py', '--exclude', 'core.py']) == 0


def test_missing_file():
    assert call_vulture(['missing.py']) == 1


def test_dir():
    assert call_vulture(['tests']) == 0


def test_whitelist_with_python():
    assert subprocess.call([sys.executable, WHITELIST], cwd=REPO) == 0


def test_whitelist_with_vulture():
    assert call_vulture([WHITELIST]) == 0


def test_pyc():
    assert call_vulture(['missing.pyc']) == 1


def test_version():
    assert call_vulture(['--version']) == 0
    assert get_output(['--version']).strip() == 'vulture ' + __version__
