from collections import defaultdict
import re

NOQA_REGEXP = re.compile(
    # Use the same regex as flake8 does.
    # https://gitlab.com/pycqa/flake8/-/tree/master/src/flake8/defaults.py
    # We're looking for items that look like this:
    # `# noqa`
    # `# noqa: E123`
    # `# noqa: E123,W451,F921`
    # `# NoQA: E123,W451,F921`
    r"# noqa(?::[\s]?(?P<codes>([A-Z]+[0-9]+(?:[,\s]+)?)+))?",
    re.IGNORECASE,
)


def parse_error_codes(match):
    # If no error code is specified, add the line to the "all" category.
    return [
        c.strip() for c in (match.groupdict()["codes"] or "all").split(",")
    ]


def parse_noqa(code):
    noqa_lines = defaultdict(set)
    for lineno, line in enumerate(code, start=1):
        match = NOQA_REGEXP.search(line)
        if match:
            for error_code in parse_error_codes(match):
                noqa_lines[error_code].add(lineno)
    return noqa_lines


def ignore_line(noqa_lines, lineno, typ):
    """Check if the reported line is annotated with "# noqa"."""
    from vulture.core import ERROR_CODES

    return (
        lineno in noqa_lines[ERROR_CODES[typ]] or lineno in noqa_lines["all"]
    )
