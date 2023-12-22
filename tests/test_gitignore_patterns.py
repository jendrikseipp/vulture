import os
import pathlib
import pytest
import shutil

from . import call_vulture
from vulture.utils import ExitCode


class TempGitignore:
    def __init__(self, patterns):
        self.patterns = patterns
        root = pathlib.Path(".").resolve()
        self.file = root / ".gitignore"
        self.tmpfile = root / ".tmp_gitignore"

    def __enter__(self):
        shutil.move(self.file, self.tmpfile)
        with open(self.file, "w") as f:
            f.write("\n".join(self.patterns))

        return self.file

    def __exit__(self, *args):
        os.remove(self.file)
        shutil.move(self.tmpfile, self.file)


@pytest.fixture(scope="function")
def gitignore(request):
    with TempGitignore(request.param) as fpath:
        yield fpath


@pytest.mark.parametrize(
    "exclude_patterns,gitignore,exit_code",
    (
        ([], [], ExitCode.NoDeadCode),
        ([""], [], ExitCode.NoDeadCode),
        ([], [""], ExitCode.NoDeadCode),
        ([""], ["core.py", "utils.py"], ExitCode.NoDeadCode),
        (["core.py", "utils.py"], [""], ExitCode.DeadCode),
        ([], ["core.py", "utils.py"], ExitCode.DeadCode),
    ),
    indirect=("gitignore",),
)
def test_gitignore(exclude_patterns, gitignore, exit_code):
    def get_csv(paths):
        return ",".join(os.path.join("vulture", path) for path in paths)

    cli_args = ["vulture/"]
    if exclude_patterns:
        cli_args.extend(["--exclude", get_csv(exclude_patterns)])

    assert gitignore.is_file()
    assert call_vulture(cli_args) == exit_code
