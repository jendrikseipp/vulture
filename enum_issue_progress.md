## Our progress thus far on [issue #304](https://github.com/jendrikseipp/vulture/issues/304)

- We traced the code path by running the debugger on the source code.
- Identified that Vulture generates an AST of the provided source code in the `scan` function in `core.py`
- Each node in the AST is then visited by the `visit` function
- The `visit` function decides what helper to use based on the type of node
- For this issue, we specifically care about the `visit_Call` and `visit_ClassDef` functions because these are invoked when the `list()` function is called, and when a class is defined with the `Enum` subclass.

Based on these findings, here is a high level approach of the solution we will implement:

- Extend the ast with scoping information using the [asttokens](https://asttokens.readthedocs.io/en/latest/) package.
- In `visit_Call`, check if the `node.func.id=='list'` - are we calling the list function?
- If so, get the argument(`node.args[0].id`) and use the scoping information provided by asttokens to check if the argument is a class
- If so, use the scope info about the class to check if `Enum` is a superclass.
- If so, then add all the fields defined in the class to `defined_variables`

Debug output is attached below. See `enum_scope.txt` for more details.

```
Module(
    body=[
        ImportFrom(
            module='enum',
            names=[
                alias(name='Enum')],
            level=0),
        ClassDef(
            name='E',
            bases=[
                Name(id='Enum', ctx=Load())],
            keywords=[],
            body=[
                Assign(
                    targets=[
                        Name(id='A', ctx=Store())],
                    value=Constant(value=1)),
                Assign(
                    targets=[
                        Name(id='B', ctx=Store())],
                    value=Constant(value=2))],
            decorator_list=[])],
    type_ignores=[])
Module(
    body=[
        Import(
            names=[
                alias(name='enum')]),
        ClassDef(
            name='EnumWhitelist',
            bases=[
                Attribute(
                    value=Name(id='enum', ctx=Load()),
                    attr='Enum',
                    ctx=Load())],
            keywords=[],
            body=[
                Assign(
                    targets=[
                        Name(id='EnumWhitelist', ctx=Store())],
                    value=Constant(value=1))],
            decorator_list=[]),
        Expr(
            value=Attribute(
                value=Attribute(
                    value=Name(id='EnumWhitelist', ctx=Load()),
                    attr='EnumWhitelist',
                    ctx=Load()),
                attr='_name_',
                ctx=Load())),
        Expr(
            value=Attribute(
                value=Attribute(
                    value=Name(id='EnumWhitelist', ctx=Load()),
                    attr='EnumWhitelist',
                    ctx=Load()),
                attr='_value_',
                ctx=Load()))],
    type_ignores=[])
enum_test.py:3: unused class 'E' (60% confidence)
enum_test.py:4: unused variable 'A' (60% confidence)
enum_test.py:5: unused variable 'B' (60% confidence)
```
