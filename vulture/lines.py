import ast
from collections import namedtuple
import sys

ENTRY_POINTS = (ast.ClassDef, ast.FunctionDef)

TRAVERSABLE_FIELDS = {
        ast.ClassDef: ('decorator_list', 'body', ),
        ast.ExceptHandler: ('body',),
        ast.For: ('body', 'orelse'),
        ast.FunctionDef: ('decorator_list', 'body',),
        ast.If: ('body', 'orelse'),
        ast.Module: ('body',),
        ast.While: ('body', 'orelse'),
        ast.With: ('body',),
}
if sys.version_info < (3, 0):
    TRAVERSABLE_FIELDS.update({
        ast.TryExcept: ('body', 'handlers', 'orelse'),
        ast.TryFinally: ('body', 'finalbody'),
    })
else:
    TRAVERSABLE_FIELDS.update({
        ast.Try: ('body', 'handlers', 'orelse', 'finalbody')
    })


def _get_range(entry):
    if isinstance(entry, ENTRY_POINTS):
        last_body = entry.body[-1]
        while isinstance(last_body, tuple(TRAVERSABLE_FIELDS.keys())):
            fields = TRAVERSABLE_FIELDS[last_body.__class__]
            for field in reversed(fields):
                children = getattr(last_body, field)
                if children:
                    break
            last_body = children[-1]  # The last child.

        last_line = last_body.lineno
        SourceRange = namedtuple("SourceRange",
                                 ['name', 'start_line', 'last_line'])
        source_range = SourceRange(entry.name, entry.lineno, last_line)
        yield source_range


def count_lines(code):
    span = 1
    for source_range in _get_range(code):
        span = (1 + source_range.last_line - source_range.start_line)
    return span
