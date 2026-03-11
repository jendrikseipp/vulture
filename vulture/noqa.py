import re
from collections import defaultdict

FLAKE8_NOQA_REGEXP = re.compile(
    # Use the same regex as flake8 does.
    # https://github.com/pycqa/flake8/blob/main/src/flake8/defaults.py
    # We're looking for items that look like this:
    # `# noqa`
    # `# noqa: E123`
    # `# noqa: E123,W451,F921`
    # `# NoQA: E123,W451,F921`
    r"# noqa(?::\s?(?P<codes>([A-Z]+[0-9]+(?:[,\s]+)?)+))?",
    re.IGNORECASE,
)

PYLINT_NOQA_REGEXP = re.compile(
    # Pylint format: # pylint: disable=unused-import
    # Also supports: # pylint: disable=unused-import,unused-variable
    # And: # pylint: disable-all
    # Note: we only parse disable, not enable (enable is more complex)
    r"# pylint:\s*disable(?:-all)?(?:\s*=\s*(?P<codes>[^#\n]+))?",
    re.IGNORECASE,
)

FLAKE8_NOQA_CODE_MAP = {
    # flake8 F401: module imported but unused.
    "F401": "V104",
    # flake8 F841: local variable is assigned to but never used.
    "F841": "V107",
}

PYLINT_NOQA_CODE_MAP = {
    # pylint unused-import: module imported but unused.
    "unused-import": "V104",
    # pylint unused-variable: local variable is assigned to but never used.
    "unused-variable": "V107",
    # pylint unused-argument: function argument is never used.
    "unused-argument": "V107",
    # pylint possibly-unused-variable: variable might be unused.
    "possibly-unused-variable": "V107",
    # pylint unreachable-code: code after return/break/continue/raise.
    "unreachable-code": "V201",
    # Pylint numeric codes (see https://pylint.readthedocs.io/en/latest/user_guide/messages/)
    "W0611": "V104",  # unused-import
    "W0612": "V107",  # unused-variable
    "W0613": "V107",  # unused-argument
    "W0641": "V107",  # possibly-unused-variable
    "W0101": "V201",  # unreachable
}


def _parse_error_codes(match):
    # If no error code is specified, add the line to the "all" category.
    return [
        c.strip() for c in (match.groupdict()["codes"] or "all").split(",")
    ]


def _parse_pylint_codes(match):
    # Parse pylint codes from "disable=code1,code2" or "disable-all"
    codes_str = match.groupdict().get("codes")

    # Check for disable-all (no codes specified or explicitly disable-all)
    if "disable-all" in match.group(0).lower() or codes_str is None:
        return ["all"]

    # Parse comma-separated codes
    return [c.strip() for c in codes_str.split(",")]


def parse_noqa(code):
    noqa_lines = defaultdict(set)
    for lineno, line in enumerate(code, start=1):
        # Parse flake8 noqa comments
        match_flake8 = FLAKE8_NOQA_REGEXP.search(line)
        if match_flake8:
            for error_code in _parse_error_codes(match_flake8):
                error_code = FLAKE8_NOQA_CODE_MAP.get(error_code, error_code)
                noqa_lines[error_code].add(lineno)
        # Parse pylint disable comments
        match_pylint = PYLINT_NOQA_REGEXP.search(line)
        if match_pylint:
            for pylint_code in _parse_pylint_codes(match_pylint):
                if pylint_code == "all":
                    # For disable-all, add to "all" category
                    noqa_lines["all"].add(lineno)
                else:
                    # Map pylint code to vulture error code
                    vulture_code = PYLINT_NOQA_CODE_MAP.get(pylint_code)
                    if vulture_code:
                        noqa_lines[vulture_code].add(lineno)
    return noqa_lines


def ignore_line(noqa_lines, lineno, error_code):
    """Check if the reported line is annotated
    with "# noqa" or "# pylint: disable=xxx"."""
    return lineno in noqa_lines[error_code] or lineno in noqa_lines["all"]
