import pytest

from vulture import Vulture


@pytest.fixture
def v():
    return Vulture(verbose=True)


def test_syntax_error(v):
    v.scan("""foo bar""")
    assert int(v.report()) == 1
