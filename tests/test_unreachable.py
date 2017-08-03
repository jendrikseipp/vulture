from . import v
assert v  # Silence pyflakes


def check_unreachable(v, lineno, size, name):
    assert len(v.unreachable_code) == 1
    item = v.unreachable_code[0]
    assert item.lineno == lineno
    assert item.size == size
    assert item.name == name


def test_assignment(v):
    v.scan("""\
def foo():
    print("Hello World")
    return
    a = 1
""")
    check_unreachable(v, 4, 1, 'return')


def test_multiline_return_statements(v):
    v.scan("""\
def foo():
    print("Something")
    return (something,
            that,
            spans,
            over,
            multiple,
            lines)
    print("Hello World")
""")
    check_unreachable(v, 9, 1, 'return')


def test_multiple_return_statements(v):
    v.scan("""\
def foo():
    return something
    return None
    return (some, statement)
""")
    check_unreachable(v, 3, 2, 'return')


def test_pass(v):
    v.scan("""\
def foo():
    return
    pass
    return something
""")
    check_unreachable(v, 3, 2, 'return')


def test_multiline_return(v):
    v.scan("""
def foo():
    return \
        "Hello"
    print("Unreachable code")
""")
    check_unreachable(v, 4, 1, 'return')


def test_recursive_functions(v):
    v.scan("""\
def foo(a):
    if a == 1:
        return 1
    else:
        return foo(a - 1)
        print("This line is never executed")
""")
    check_unreachable(v, 6, 1, 'return')


def test_semicolon(v):
    v.scan("""\
def foo():
    return; a = 1
""")
    check_unreachable(v, 2, 1, 'return')


def test_list(v):
    v.scan("""\
def foo(a):
    return
    a[1:2]
""")
    check_unreachable(v, 3, 1, 'return')


def test_continue(v):
    v.scan("""\
def foo():
    if foo():
        return True
        continue
    else:
        return False
""")
    check_unreachable(v, 4, 1, 'return')
