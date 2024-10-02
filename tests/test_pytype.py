import subprocess
from subprocess import PIPE

def test_pytype():
    result = subprocess.run(
        ['pytype', 'vulture/core.py', '--disable=attribute-error'],
        stdout=PIPE, stderr=PIPE, universal_newlines=True
    )
    assert result.stdout.strip().endswith('Success: no errors found')