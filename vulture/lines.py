import ast
import sys

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


def get_last_line_number(node):
    last_body = node.body[-1]
    while isinstance(last_body, tuple(TRAVERSABLE_FIELDS.keys())):
        fields = TRAVERSABLE_FIELDS[last_body.__class__]
        for field in reversed(fields):
            children = getattr(last_body, field)
            if children:
                break
        last_body = children[-1]

    return last_body.lineno


def count_lines(node):
    return get_last_line_number(node) - node.lineno + 1
