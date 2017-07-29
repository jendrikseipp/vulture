from . import check, v


def test_old_format_string(v):
    v.scan("'%(a)s, %(b)d' % locals()")
    check(v.used_names, ['a', 'b', 'locals'])


def test_new_format_string(v):
    v.scan("'{a}, {b:0d} {c:<30} {d:.2%}'.format(**locals())")
    check(v.used_names, ['a', 'b', 'c', 'd', 'locals'])
