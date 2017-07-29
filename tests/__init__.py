import pytest
from vulture import Vulture


@pytest.fixture
def v():
    return Vulture(verbose=True)


def check(items_or_names, expected_names):
    if isinstance(items_or_names, set):
        # items_or_names is a set of strings.
        assert items_or_names == set(expected_names)
    else:
        # items_or_names is a list of Item objects.
        names = sorted(item.name for item in items_or_names)
        expected_names = sorted(expected_names)
        assert names == expected_names
