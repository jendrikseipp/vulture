from . import check_multiple_unreachable, check_unreachable, v

assert v  # Silence pyflakes


def test_return_assignment(v):
    v.scan(
        """\
def foo():
    print("Hello World")
    return
    a = 1
"""
    )
    check_unreachable(v, 4, 1, "return")


def test_return_multiline_return_statements(v):
    v.scan(
        """\
def foo():
    print("Something")
    return (something,
            that,
            spans,
            over,
            multiple,
            lines)
    print("Hello World")
"""
    )
    check_unreachable(v, 9, 1, "return")


def test_return_multiple_return_statements(v):
    v.scan(
        """\
def foo():
    return something
    return None
    return (some, statement)
"""
    )
    check_unreachable(v, 3, 2, "return")


def test_return_pass(v):
    v.scan(
        """\
def foo():
    return
    pass
    return something
"""
    )
    check_unreachable(v, 3, 2, "return")


def test_return_multiline_return(v):
    v.scan(
        """
def foo():
    return \
        "Hello"
    print("Unreachable code")
"""
    )
    check_unreachable(v, 4, 1, "return")


def test_return_recursive_functions(v):
    v.scan(
        """\
def foo(a):
    if a == 1:
        return 1
    else:
        return foo(a - 1)
        print("This line is never executed")
"""
    )
    check_unreachable(v, 6, 1, "return")


def test_return_semicolon(v):
    v.scan(
        """\
def foo():
    return; a = 1
"""
    )
    check_unreachable(v, 2, 1, "return")


def test_return_list(v):
    v.scan(
        """\
def foo(a):
    return
    a[1:2]
"""
    )
    check_unreachable(v, 3, 1, "return")


def test_return_continue(v):
    v.scan(
        """\
def foo():
    if foo():
        return True
        continue
    else:
        return False
"""
    )
    check_unreachable(v, 4, 1, "return")


def test_return_function_definition(v):
    v.scan(
        """\
def foo():
    return True
    def bar():
        return False
"""
    )
    check_unreachable(v, 3, 2, "return")


def test_raise_global(v):
    v.scan(
        """\
raise ValueError
a = 1
"""
    )
    check_unreachable(v, 2, 1, "raise")


def test_raise_assignment(v):
    v.scan(
        """\
def foo():
    raise ValueError
    li = []
"""
    )
    check_unreachable(v, 3, 1, "raise")


def test_multiple_raise_statements(v):
    v.scan(
        """\
def foo():
    a = 1
    raise
    raise KeyError
    # a comment
    b = 2
    raise CustomDefinedError
"""
    )
    check_unreachable(v, 4, 4, "raise")


def test_return_with_raise(v):
    v.scan(
        """\
def foo():
    a = 1
    return
    raise ValueError
    return
"""
    )
    check_unreachable(v, 4, 2, "return")


def test_return_comment_and_code(v):
    v.scan(
        """\
def foo():
    return
    # This is a comment
    print("Hello World")
"""
    )
    check_unreachable(v, 4, 1, "return")


def test_raise_with_return(v):
    v.scan(
        """\
def foo():
    a = 1
    raise
    return a
"""
    )
    check_unreachable(v, 4, 1, "raise")


def test_raise_error_message(v):
    v.scan(
        """\
def foo():
    raise SomeError("There is a problem")
    print("I am unreachable")
"""
    )
    check_unreachable(v, 3, 1, "raise")


def test_raise_try_except(v):
    v.scan(
        """\
def foo():
    try:
        a = 1
        raise
    except IOError as e:
        print("We have some problem.")
        raise
        print(":-(")
"""
    )
    check_unreachable(v, 8, 1, "raise")


def test_raise_with_comment_and_code(v):
    v.scan(
        """\
def foo():
    raise
    # This is a comment
    print("Something")
    return None
"""
    )
    check_unreachable(v, 4, 2, "raise")


def test_continue_basic(v):
    v.scan(
        """\
def foo():
    if bar():
        a = 1
    else:
        continue
        a = 2
"""
    )
    check_unreachable(v, 6, 1, "continue")


def test_continue_one_liner(v):
    v.scan(
        """\
def foo():
    for i in range(1, 10):
        if i == 5: continue
        print(1 / i)
"""
    )
    assert v.unreachable_code == []


def test_continue_nested_loops(v):
    v.scan(
        """\
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
"""
    )
    check_unreachable(v, 9, 1, "continue")


def test_continue_with_comment_and_code(v):
    v.scan(
        """\
def foo():
    if bar1():
        bar2()
    else:
        a = 1
        continue
        # Just a comment
        raise ValueError
"""
    )
    check_unreachable(v, 8, 1, "continue")


def test_break_basic(v):
    v.scan(
        """\
def foo():
    for i in range(123):
        break
        # A comment
        return
        dead = 1
"""
    )
    check_unreachable(v, 5, 2, "break")


def test_break_one_liner(v):
    v.scan(
        """\
def foo():
    for i in range(10):
        if i == 3: break
        print(i)
"""
    )
    assert v.unreachable_code == []


def test_break_with_comment_and_code(v):
    v.scan(
        """\
while True:
    break
    # some comment
    print("Hello")
"""
    )
    check_unreachable(v, 4, 1, "break")


def test_if_false(v):
    v.scan(
        """\
if False:
    pass
"""
    )
    check_unreachable(v, 1, 2, "if")


def test_elif_false(v):
    v.scan(
        """\
if bar():
    pass
elif False:
    print("Unreachable")
"""
    )
    check_unreachable(v, 3, 2, "if")


def test_nested_if_statements_false(v):
    v.scan(
        """\
if foo():
    if bar():
        pass
    elif False:
        print("Unreachable")
        pass
    elif something():
        print("Reachable")
    else:
        pass
else:
    pass
"""
    )
    check_unreachable(v, 4, 3, "if")


def test_if_false_same_line(v):
    v.scan(
        """\
if False: a = 1
else: c = 3
"""
    )
    check_unreachable(v, 1, 1, "if")


def test_if_true(v):
    v.scan(
        """\
if True:
    a = 1
    b = 2
else:
    c = 3
    d = 3
"""
    )
    # For simplicity, we don't report the "else" line as dead code.
    check_unreachable(v, 5, 2, "else")


def test_if_true_same_line(v):
    v.scan(
        """\
if True:
    a = 1
    b = 2
else: c = 3
d = 3
"""
    )
    check_unreachable(v, 4, 1, "else")


def test_nested_if_statements_true(v):
    v.scan(
        """\
if foo():
    if bar():
        pass
    elif True:
        if something():
            pass
        else:
            pass
    elif something_else():
        print("foo")
    else:
        print("bar")
else:
    pass
"""
    )
    check_unreachable(v, 9, 4, "else")


def test_redundant_if(v):
    v.scan(
        """\
if [5]:
    pass
"""
    )
    print(v.unreachable_code[0].size)
    check_unreachable(v, 1, 2, "if")


def test_if_exp_true(v):
    v.scan("foo if True else bar")
    check_unreachable(v, 1, 1, "ternary")


def test_if_exp_false(v):
    v.scan("foo if False else bar")
    check_unreachable(v, 1, 1, "ternary")


def test_if_true_return(v):
    v.scan(
        """\
def foo(a):
    if True:
        return 0
    print(":-(")
"""
    )
    check_multiple_unreachable(v, [(2, 2, "if"), (4, 1, "if")])


def test_if_true_return_else(v):
    v.scan(
        """\
def foo(a):
    if True:
        return 0
    else:
        return 1
    print(":-(")
"""
    )
    check_multiple_unreachable(v, [(5, 1, "else"), (6, 1, "if")])


def test_if_some_branches_return(v):
    v.scan(
        """\
def foo(a):
    if a == 0:
        return 0
    elif a == 1:
        pass
    else:
        return 2
    print(":-(")
"""
    )
    assert v.unreachable_code == []


def test_if_all_branches_return(v):
    v.scan(
        """\
def foo(a):
    if a == 0:
        return 0
    elif a == 1:
        return 1
    else:
        return 2
    print(":-(")
"""
    )
    check_unreachable(v, 8, 1, "if")


def test_if_all_branches_return_nested(v):
    v.scan(
        """\
def foo(a, b):
    if a:
        if b:
            return 1
        return 2
    else:
        return 3
    print(":-(")
"""
    )
    check_unreachable(v, 8, 1, "if")


def test_if_all_branches_return_or_raise(v):
    v.scan(
        """\
def foo(a):
    if a == 0:
        return 0
    else:
        raise Exception()
    print(":-(")
"""
    )
    check_unreachable(v, 6, 1, "if")


def test_try_fall_through(v):
    v.scan(
        """\
def foo():
    try:
        pass
    except IndexError as e:
        raise e
    print(":-(")
"""
    )
    assert v.unreachable_code == []


def test_try_some_branches_raise(v):
    v.scan(
        """\
def foo(e):
    try:
        raise e
    except IndexError as e:
        pass
    except Exception as e:
        raise e
    print(":-(")
"""
    )
    assert v.unreachable_code == []


def test_try_all_branches_return_or_raise(v):
    v.scan(
        """\
def foo():
    try:
        return 2
    except IndexError as e:
        raise e
    except Exception as e:
        raise e
    print(":-(")
"""
    )
    check_unreachable(v, 8, 1, "try")


def test_try_nested_no_fall_through(v):
    v.scan(
        """\
def foo(a):
    try:
        raise a
    except:
        try:
            return
        except Exception as e:
            raise e
    print(":-(")
"""
    )
    check_unreachable(v, 9, 1, "try")


def test_try_reachable_else(v):
    v.scan(
        """\
def foo():
    try:
        print(":-)")
    except:
        return 1
    else:
        print(":-(")
"""
    )
    assert v.unreachable_code == []


def test_try_unreachable_else(v):
    v.scan(
        """\
def foo():
    try:
        raise Exception()
    except Exception as e:
        return 1
    else:
        print(":-(")
"""
    )
    check_unreachable(v, 7, 1, "else")


def test_with_fall_through(v):
    v.scan(
        """\
def foo(a):
    with a():
        raise Exception()
    print(":-(")
"""
    )
    assert v.unreachable_code == []


def test_async_with_fall_through(v):
    v.scan(
        """\
async def foo(a):
    async with a():
        raise Exception()
    print(":-(")
"""
    )
    assert v.unreachable_code == []


def test_for_fall_through(v):
    v.scan(
        """\
def foo(a):
    for i in a:
        raise Exception()
    print(":-(")
"""
    )
    assert v.unreachable_code == []


def test_async_for_fall_through(v):
    v.scan(
        """\
async def foo(a):
    async for i in a:
        raise Exception()
    print(":-(")
"""
    )
    assert v.unreachable_code == []


def test_while_false(v):
    v.scan(
        """\
while False:
    pass
"""
    )
    check_unreachable(v, 1, 2, "while")


def test_while_nested(v):
    v.scan(
        """\
while True:
    while False:
        pass
"""
    )
    check_unreachable(v, 2, 2, "while")


def test_while_true_else(v):
    v.scan(
        """\
while True:
    print("I won't stop")
else:
    print("I won't run")
"""
    )
    check_unreachable(v, 4, 1, "else")


def test_while_true_no_fall_through(v):
    v.scan(
        """\
while True:
    raise Exception() 
print(":-(")
"""
    )
    check_unreachable(v, 3, 1, "while")


def test_while_true_no_fall_through_nested(v):
    v.scan(
        """\
while True:
    if a > 3:
        raise Exception() 
    else:
        pass
print(":-(")
"""
    )
    check_unreachable(v, 6, 1, "while")


def test_while_true_no_fall_through_nested_loops(v):
    v.scan(
        """\
while True:
    for _ in range(3):
        break
    while False:
        break
print(":-(")
"""
    )
    check_multiple_unreachable(v, [(4, 2, "while"), (6, 1, "while")])


def test_while_true_fall_through(v):
    v.scan(
        """\
while True:
    break 
print(":-)")
"""
    )
    assert v.unreachable_code == []


def test_while_true_fall_through_nested(v):
    v.scan(
        """\
while True:
    if a > 3:
        raise Exception() 
    else:
        break
print(":-(")
"""
    )
    assert v.unreachable_code == []


def test_while_fall_through(v):
    v.scan(
        """\
def foo(a):
    while a > 0:
        return 1
    print(":-)")
"""
    )
    assert v.unreachable_code == []
