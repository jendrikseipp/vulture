# -*- coding: utf-8 -*-
#
# vulture - Find dead code.
#
# Copyright (c) 2012-2020 Jendrik Seipp (jendrikseipp@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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

NOQA_CODE_MAP = {
    # flake8 F401: module imported but unused.
    "F401": "V104",
    # flake8 F841: local variable is assigned to but never used.
    "F841": "V107",
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
