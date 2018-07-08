import os.path
import subprocess

import pytest
from vulture.coverage_xml import detect_used_funcs

from . import check, v
assert v  # Silence pyflakes.


@pytest.fixture
def check_whitelist(v, tmpdir):
    def test_created_whitelist(code, expected):
        sample = os.path.normcase(str(tmpdir.join("unused_code.py")))
        xml = str(tmpdir.join("coverage.xml"))
        with open(sample, 'w') as f:
            f.write(code)
        subprocess.call(["coverage", "run", sample])
        subprocess.call(["coverage", "xml", "-o", xml])
        v.scavenge([sample])
        whitelist = set(item for item in detect_used_funcs(v, xml))
        check(whitelist, expected)
    return test_created_whitelist


def test_getattr_function(check_whitelist):
    code = """\
class Greeter:
    def greet(self):
        print("Hi")
greeter = Greeter()
greet_func = getattr(greeter, "greet")
greet_func()
"""
    expected = ['greet']
    check_whitelist(code, expected)


def test_getattr_method(check_whitelist):
    code = """\
class Greeter:
    def __init__(self):
        greeter = getattr(self, 'greet')
        greeter()

    def greet(self):
        print('Hi')
Greeter()
"""
    expected = ['greet']
    check_whitelist(code, expected)
