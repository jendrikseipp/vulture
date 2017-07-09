import glob
import os.path
import subprocess
import sys

from vulture import __version__

DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(DIR)
WHITELISTS = glob.glob(os.path.join(REPO, 'vulture', 'whitelists', '*.py'))


def call_vulture(args, **kwargs):
    core = 'vulture'
    if sys.version_info < (2, 7):
        core = 'vulture.core'
    return subprocess.call(
        [sys.executable, '-m', core] + args, cwd=REPO, **kwargs)


def get_output(args):
    child = subprocess.Popen([sys.executable, "vulture/core.py"] + args,
                             cwd=REPO, stdout=subprocess.PIPE)
    return child.communicate()[0].decode("utf-8")


def test_script_with_explicit_whitelist():
    for whitelist in WHITELISTS:
        assert call_vulture(['vulture/core.py', whitelist]) == 0


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
    for whitelist in WHITELISTS:
        assert subprocess.call([sys.executable, whitelist], cwd=REPO) == 0


def test_pyc():
    assert call_vulture(['missing.pyc']) == 1


def test_version():
    assert call_vulture(['--version']) == 0
    assert get_output(['--version']).strip() == 'vulture ' + __version__


def test_module():
    assert call_vulture(['vulture']) == 0
