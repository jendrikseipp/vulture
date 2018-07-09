import os.path
import subprocess
import sys

from . import call_vulture, REPO, WHITELISTS


def call_coverage(args, **kwargs):
    return subprocess.call(
            [sys.executable, '-m', 'coverage'] + args, cwd=REPO, **kwargs)


def test_module_with_explicit_whitelists():
    assert call_vulture(['vulture/'] + WHITELISTS) == 0


def test_module_with_implicit_whitelists():
    assert call_vulture(['vulture/']) == 0


def test_module_without_whitelists():
    assert call_vulture(['vulture/', '--exclude', 'whitelists']) == 1


def test_missing_file():
    assert call_vulture(['missing.py']) == 1


def test_tests():
    assert call_vulture(['tests/']) == 0


def test_whitelists_with_python():
    for whitelist in WHITELISTS:
        assert subprocess.call([sys.executable, whitelist], cwd=REPO) == 0


def test_pyc():
    assert call_vulture(['missing.pyc']) == 1


def test_sort_by_size():
    assert call_vulture(['vulture/utils.py', '--sort-by-size']) == 1


def test_min_confidence():
    assert call_vulture([
        'vulture/core.py', '--exclude', 'whitelists',
        '--min-confidence', '100']) == 0


def test_exclude():
    def get_csv(paths):
        return ",".join(os.path.join('vulture', path) for path in paths)

    def call_vulture_with_excludes(excludes):
        return call_vulture(['vulture/', '--exclude', get_csv(excludes)])

    assert call_vulture_with_excludes(['core.py', 'utils.py']) == 1
    assert call_vulture_with_excludes(
            ['core.py', 'utils.py', 'lines.py', 'coverage_xml.py']) == 0


def test_make_whitelist():
    assert call_vulture(
            ['vulture/', '--make-whitelist', '--exclude', 'whitelists']) == 1
    assert call_vulture(['vulture/', '--make-whitelist']) == 0


def test_coverage_xml(tmpdir):
    xml = str(tmpdir.join("coverage.xml"))
    tmp_whitelist = str(tmpdir.join("tmp_whitelist.py"))
    call_coverage(["run", "-m", "vulture", "vulture/", "tests/"])
    call_coverage(["xml", "-o", xml])
    with open(tmp_whitelist, 'w') as f:
        f.write("""\
visit_arg  # ast.arg was added in Python 3.0.
visit_AsyncFunctionDef  # no async function used in Vulture.
""")
    assert call_vulture(
        ['vulture/', 'tests/', tmp_whitelist, '--exclude', 'whitelists',
         '--coverage-xml', xml]) == 0
