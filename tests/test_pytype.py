import subprocess


def test_pytype():
    result = subprocess.run(
        ["pytype", "vulture/core.py", "--disable=attribute-error"],
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip().endswith("Success: no errors found")
