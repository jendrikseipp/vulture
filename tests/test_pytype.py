import subprocess
import sys

import pytest


@pytest.mark.skipif(
    sys.version_info >= (3, 13), reason="needs Python < 3.13 for pytype"
)
def test_pytype():
    assert subprocess.run(["pytype", "vulture/core.py"]).returncode == 0
