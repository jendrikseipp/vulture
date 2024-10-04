import subprocess
import sys
import pytest


@pytest.mark.skipif(
    sys.version_info >= (3, 13), reason="Need python < 3.13 for pytype"
)
def test_pytype():
    result = subprocess.run(
        ["pytype", "vulture/core.py", "--disable=attribute-error"],
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip().endswith("Success: no errors found")
