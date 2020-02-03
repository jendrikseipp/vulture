"""

Vulture sometimes reports used code as unused. To avoid these
false-positives, you can write a Python file that explicitly uses the
code and pass it to vulture:

vulture myscript.py mydir mywhitelist.py

When creating a whitelist file, you have to make sure not to write code
that hides unused code in other files. E.g., this is why we don't import
and access the "sys" module below. If we did import it, vulture would
not be able to detect whether other files import "sys" without using it.

This file explicitly uses code from the Python standard library that is
often incorrectly detected as unused.

"""


class Whitelist:
    """
    Helper class that allows mocking Python objects.

    Use it to create whitelist files that are not only syntactically
    correct, but can also be executed.

    """

    def __getattr__(self, _):
        pass


assert Whitelist
