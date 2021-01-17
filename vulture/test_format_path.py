"""
test_format_path

temporary testing for vulture.utils.format_path
"""
import sys

from vulture.utils import format_path

if __name__ == "__main__":
    for format_id in ("relative", "absolute"):
        result = format_path(
            "vulture/test_format_path.py", None, format_id=format_id
        )
        print(f"{format_id}: {result}", file=sys.stderr, flush=True)
