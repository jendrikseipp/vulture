from . import check, v
assert v  # Silence pyflakes.


def test_old_format_string(v):
    v.scan("'%(a)s, %(b)d' % locals()")
    check(v.used_names, ['a', 'b', 'locals'])


def test_new_format_string(v):
    v.scan("'{a}, {b:0d} {c:<30} {d:.2%}'.format(**locals())")
    check(v.used_names, ['a', 'b', 'c', 'd', 'locals'])


def test_new_format_string_access(v):
    v.scan("'{a.b}, {c.d.e} {f[g]} {h[i][j]}'.format(**locals())")
    check(v.used_names, ['a', 'c', 'f', 'h', 'locals'])


def test_new_format_string_attributes(v):
    v.scan("'{a.b}, {c.d.e} {f[g]} {h[i][j].k}'.format(**locals())")
    check(v.used_names, ['a', 'c', 'f', 'h', 'locals'])
    check(v.used_attrs, ['b', 'd', 'e', 'k', 'format'])


def test_new_format_string_numbers(v):
    v.scan("'{0.b}, {0.d.e} {0[1]} {0[1][1].k}'.format('foo')")
    check(v.used_names, [])
    check(v.used_attrs, ['b', 'd', 'e', 'k', 'format'])


def test_incorrect_format_string(v):
    v.scan('"{"')
    v.scan('"{!-a:}"')
    check(v.used_names, [])
    check(v.used_attrs, [])
