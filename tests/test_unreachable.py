from . import check_unreachable
from . import v
assert v  # Silence pyflakes


def test_return_assignment(v):
    v.scan("""\
def foo():
    print("Hello World")
    return
    a = 1
""")
    check_unreachable(v, 4, 1, 'return')


def test_return_multiline_return_statements(v):
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


def test_return_multiple_return_statements(v):
    v.scan("""\
def foo():
    return something
    return None
    return (some, statement)
""")
    check_unreachable(v, 3, 2, 'return')


def test_return_pass(v):
    v.scan("""\
def foo():
    return
    pass
    return something
""")
    check_unreachable(v, 3, 2, 'return')


def test_return_multiline_return(v):
    v.scan("""
def foo():
    return \
        "Hello"
    print("Unreachable code")
""")
    check_unreachable(v, 4, 1, 'return')


def test_return_recursive_functions(v):
    v.scan("""\
def foo(a):
    if a == 1:
        return 1
    else:
        return foo(a - 1)
        print("This line is never executed")
""")
    check_unreachable(v, 6, 1, 'return')


def test_return_semicolon(v):
    v.scan("""\
def foo():
    return; a = 1
""")
    check_unreachable(v, 2, 1, 'return')


def test_return_list(v):
    v.scan("""\
def foo(a):
    return
    a[1:2]
""")
    check_unreachable(v, 3, 1, 'return')


def test_return_continue(v):
    v.scan("""\
def foo():
    if foo():
        return True
        continue
    else:
        return False
""")
    check_unreachable(v, 4, 1, 'return')


def test_raise_assignment(v):
    v.scan("""\
def foo():
    raise ValueError
    li = []
""")
    check_unreachable(v, 3, 1, 'raise')


def test_multiple_raise_statements(v):
    v.scan("""\
def foo():
    a = 1
    raise
    raise KeyError
    # a comment
    b = 2
    raise CustomDefinedError
""")
    check_unreachable(v, 4, 4, 'raise')


def test_return_with_raise(v):
    v.scan("""\
def foo():
    a = 1
    return
    raise ValueError
    return
""")
    check_unreachable(v, 4, 2, 'return')


def test_return_comment_and_code(v):
    v.scan("""\
def foo():
    return
    # This is a comment
    print("Hello World")
""")
    check_unreachable(v, 4, 1, 'return')


def test_raise_with_return(v):
    v.scan("""\
def foo():
    a = 1
    raise
    return a
""")
    check_unreachable(v, 4, 1, 'raise')


def test_raise_error_message(v):
    v.scan("""\
def foo():
    raise SomeError("There is a problem")
    print("I am unreachable")
""")
    check_unreachable(v, 3, 1, 'raise')


def test_raise_try_except(v):
    v.scan("""\
def foo():
    try:
        a = 1
        raise
    except IOError as e:
        print("We have some problem.")
        raise
        print(":-(")
""")
    check_unreachable(v, 8, 1, 'raise')


def test_raise_with_comment_and_code(v):
    v.scan("""\
def foo():
    raise
    # This is a comment
    print("Something")
    return None
""")
    check_unreachable(v, 4, 2, 'raise')


def test_continue_basic(v):
    v.scan("""\
def foo():
    if bar():
        a = 1
    else:
        continue
        a = 2
""")
    check_unreachable(v, 6, 1, 'continue')


def test_continue_one_liner(v):
    v.scan("""\
def foo():
    for i in range(1, 10):
        if i == 5: continue
        print(1 / i)
""")
    assert v.unreachable_code == []


def test_continue_nested_loops(v):
    v.scan("""\
def foo():
    a = 0
    if something():
        foo()
        if bar():
            a = 2
            continue
            # This is unreachable
            a = 1
        elif a == 1:
            pass
        else:
            a = 3
            continue
    else:
        continue
""")
    check_unreachable(v, 9, 1, 'continue')


def test_continue_with_comment_and_code(v):
    v.scan("""\
def foo():
    if bar1():
        bar2()
    else:
        a = 1
        continue
        # Just a comment
        raise ValueError
""")
    check_unreachable(v, 8, 1, 'continue')


def test_break_basic(v):
    v.scan("""\
def foo():
    for i in range(123):
        break
        # A comment
        return
        dead = 1
""")
    check_unreachable(v, 5, 2, 'break')


def test_break_one_liner(v):
    v.scan("""\
def foo():
    for i in range(10):
        if i == 3: break
        print(i)
""")
    assert v.unreachable_code == []


def test_break_with_comment_and_code(v):
    v.scan("""\
while True:
    break
    # some comment
    print("Hello")
""")
    check_unreachable(v, 4, 1, 'break')


def test_while_true_else(v):
    v.scan("""\
while True:
    print("I won't stop")
else:
    print("I won't run")
""")
    check_unreachable(v, 4, 1, 'else')
