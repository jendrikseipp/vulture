from . import check, v

assert v  # Silence pyflakes.


def test_old_format_string(v):
    v.scan("'%(a)s, %(b)d' % locals()")
    check(v.used_names, ["a", "b", "locals"])


def test_new_format_string(v):
    v.scan("'{a}, {b:0d} {c:<30} {d:.2%}'.format(**locals())")
    check(v.used_names, ["a", "b", "c", "d", "format", "locals"])


def test_f_string(v):
    v.scan(
        """\
f'{a}, {b:0d} {c:<30} {d:.2%} {e()} {f:{width}.{precision}}'
f'{ {x:y for (x, y) in ((1, 2), (3, 4))} }'
"""
    )
    check(
        v.used_names,
        ["a", "b", "c", "d", "e", "f", "precision", "width", "x", "y"],
    )


def test_new_format_string_access(v):
    v.scan("'{a.b}, {c.d.e} {f[g]} {h[i][j].k}'.format(**locals())")
    check(
        v.used_names,
        ["a", "b", "c", "d", "e", "f", "h", "k", "format", "locals"],
    )


def test_new_format_string_numbers(v):
    v.scan("'{0.b}, {0.d.e} {0[1]} {0[1][1].k}'.format(**locals())")
    check(v.used_names, ["b", "d", "e", "k", "format", "locals"])


def test_incorrect_format_string(v):
    v.scan('"{"')
    v.scan('"{!-a:}"')
    check(v.used_names, [])


def test_format_string_not_using_locals(v):
    """Strings that are not formatted with locals() should not be parsed."""
    v.scan(
        """\
"{variable}"

def foobar():
    '''
    Return data of the form
        {this_looks_like_a_format_string: 1}
    '''
    pass

"%(thing)s" % {"thing": 1}

"%(apple)s" * locals()

"{} {a} {b}".format(1, a=used_var, b=locals())
    """
    )
    check(v.used_names, ["used_var", "locals", "format"])
