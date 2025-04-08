import re
from collections import defaultdict

NOQA_REGEXP = re.compile(
    # Use the same regex as flake8 does.
    # https://github.com/pycqa/flake8/blob/main/src/flake8/defaults.py
    # We're looking for items that look like this:
    # `# noqa`
    # `# noqa: E123`
    # `# noqa: E123,W451,F921`
    # `# NoQA: E123,W451,F921`
    r"# noqa(?::[\s]?(?P<codes>([A-Z]+[0-9]+(?:[,\s]+)?)+))?",
    re.IGNORECASE,
)

NOQA_CODE_MAP = {
    # flake8 F401: module imported but unused.
    "F401": "V104",
    # flake8 F841: local variable is assigned to but never used.
    "F841": "V107",
    # ruff/flake8-unused-arguments ARG001: Unused function argument
    "ARG001": "V107",
    # ruff/flake8-unused-arguments ARG002: Unused method argument
    "ARG002": "V107",
    # ruff/flake8-unused-arguments ARG003: Unused class method argument
    "ARG003": "V107",
    # ruff/flake8-unused-arguments ARG004: Unused static method argument
    "ARG004": "V107",
    # ruff/flake8-unused-arguments ARG005: Unused lambda argument
    "ARG005": "V107",
}


def _parse_error_codes(match):
    # If no error code is specified, add the line to the "all" category.
    return [
        c.strip() for c in (match.groupdict()["codes"] or "all").split(",")
    ]


def parse_noqa(code):
    noqa_lines = defaultdict(set)
    for lineno, line in enumerate(code, start=1):
        match = NOQA_REGEXP.search(line)
        if match:
            for error_code in _parse_error_codes(match):
                error_code = NOQA_CODE_MAP.get(error_code, error_code)
                noqa_lines[error_code].add(lineno)
    return noqa_lines


def ignore_line(noqa_lines, lineno, error_code):
    """Check if the reported line is annotated with "# noqa"."""
    return lineno in noqa_lines[error_code] or lineno in noqa_lines["all"]
