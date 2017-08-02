from . import v


def check_unreachable_lines(assertion, asserted):
    unreachable_lines = [node.lineno for node in assertion]
    assert unreachable_lines == asserted


def test_assignment(v):
    v.scan("""\
def foo():
    print("Hello World")
    return
    a = 1
""")
    check_unreachable_lines(v.unreachable_code, [4])


def test_multiline_return_statements(v):
    v.scan("""\
def foo():
    print("Something")
    return (Something,
            that,
            spans,
            over,
            multiple,
            lines)
    print("Hello World")
""")
    check_unreachable_lines(v.unreachable_code, [9])


def test_multiple_return_statements(v):
    v.scan("""\
def foo():
    return something
    return None
    return (Some,
           big,
           statemnt)
""")
    check_unreachable_lines(v.unreachable_code, [3, 4])


def test_pass(v):
    v.scan("""\
def foo():
    return
    pass
    return Something
""")
    check_unreachable_lines(v.unreachable_code, [3])


def test_recursive_functions(v):
    v.scan("""\
def foo(a):
    if a == 1:
        return 1
    else:
        return foo(a-1)
        print("This line is never executed")
""")
    check_unreachable_lines(v.unreachable_code, [6])
