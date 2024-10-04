import subprocess
import sys

import pytest


@pytest.mark.skipif(
    sys.version_info >= (3, 13), reason="needs Python < 3.13 for pytype"
)
def test_pytype():
    result = subprocess.run(
        ["pytype", "vulture/core.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip().endswith("Success: no errors found")
