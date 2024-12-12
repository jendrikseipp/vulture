import ast

from vulture import utils


class Reachability:
    def __init__(self, report):
        self._report = report
        self._no_fall_through_nodes = set()

        # Since we visit the children nodes first, we need to maintain a flag
        # that indicates if a break statement was seen. When visiting the
        # parent (While, For or AsyncFor), the value is checked (for While)
        # and reset. Assumes code is valid (break statements only in loops).
        self._current_loop_has_break_statement = False

    def visit(self, node):
        """When called, all children of this node have already been visited."""
        if isinstance(node, (ast.Break, ast.Continue, ast.Return, ast.Raise)):
            self._mark_as_no_fall_through(node)
            if isinstance(node, ast.Break):
                self._current_loop_has_break_statement = True

        elif isinstance(
            node,
            (
                ast.Module,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.With,
                ast.AsyncWith,
            ),
        ):
            self._can_fall_through_statements_analysis(node.body)
        elif isinstance(node, ast.While):
            self._handle_reachability_while(node)
            self._current_loop_has_break_statement = False
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            self._can_fall_through_statements_analysis(node.body)
            self._current_loop_has_break_statement = False
        elif isinstance(node, ast.If):
            self._handle_reachability_if(node)
        elif isinstance(node, ast.IfExp):
            self._handle_reachability_if_expr(node)
        elif isinstance(node, ast.Try):
            self._handle_reachability_try(node)

    def reset(self):
        self._no_fall_through_nodes = set()

    def _can_fall_through(self, node):
        return node not in self._no_fall_through_nodes

    def _mark_as_no_fall_through(self, node):
        self._no_fall_through_nodes.add(node)

    def _can_fall_through_statements_analysis(self, statements):
        """Report unreachable statements.
        Return True if we can execute the full list of statements.
        """
        for idx, statement in enumerate(statements):
            if not self._can_fall_through(statement):
                try:
                    next_sibling = statements[idx + 1]
                except IndexError:
                    next_sibling = None
                if next_sibling is not None:
                    class_name = statement.__class__.__name__.lower()
                    self._report(
                        name=class_name,
                        first_node=next_sibling,
                        last_node=statements[-1],
                        message=f"unreachable code after '{class_name}'",
                    )
                return False
        return True

    def _handle_reachability_if(self, node):
        has_else = bool(node.orelse)

        if utils.condition_is_always_false(node.test):
            self._report(
                name="if",
                first_node=node,
                last_node=node.body
                if isinstance(node, ast.IfExp)
                else node.body[-1],
                message="unsatisfiable 'if' condition",
            )
            if_can_fall_through = True
            else_can_fall_through = self._can_else_fall_through(
                node.orelse, condition_always_true=False
            )

        elif utils.condition_is_always_true(node.test):
            if_can_fall_through = self._can_fall_through_statements_analysis(
                node.body
            )
            else_can_fall_through = self._can_else_fall_through(
                node.orelse, condition_always_true=True
            )

            if has_else:
                self._report(
                    name="else",
                    first_node=node.orelse[0],
                    last_node=node.orelse[-1],
                    message="unreachable 'else' block",
                )
            else:
                # Redundant if-condition without else block.
                self._report(
                    name="if",
                    first_node=node,
                    message="redundant if-condition",
                )
        else:
            if_can_fall_through = self._can_fall_through_statements_analysis(
                node.body
            )
            else_can_fall_through = self._can_else_fall_through(
                node.orelse, condition_always_true=False
            )

        statement_can_fall_through = (
            if_can_fall_through or else_can_fall_through
        )

        if not statement_can_fall_through:
            self._mark_as_no_fall_through(node)

    def _can_else_fall_through(self, orelse, condition_always_true):
        if not orelse:
            return not condition_always_true
        return self._can_fall_through_statements_analysis(orelse)

    def _handle_reachability_if_expr(self, node):
        if utils.condition_is_always_false(node.test):
            self._report(
                name="ternary",
                first_node=node,
                last_node=node.body
                if isinstance(node, ast.IfExp)
                else node.body[-1],
                message="unsatisfiable 'ternary' condition",
            )
        elif utils.condition_is_always_true(node.test):
            else_body = node.orelse
            self._report(
                name="ternary",
                first_node=else_body,
                message="unreachable 'else' expression",
            )

    def _handle_reachability_while(self, node):
        if utils.condition_is_always_false(node.test):
            self._report(
                name="while",
                first_node=node,
                last_node=node.body
                if isinstance(node, ast.IfExp)
                else node.body[-1],
                message="unsatisfiable 'while' condition",
            )

        elif utils.condition_is_always_true(node.test):
            else_body = node.orelse
            if else_body:
                self._report(
                    name="else",
                    first_node=else_body[0],
                    last_node=else_body[-1],
                    message="unreachable 'else' block",
                )

            if not self._current_loop_has_break_statement:
                self._mark_as_no_fall_through(node)

        self._can_fall_through_statements_analysis(node.body)

    def _handle_reachability_try(self, node):
        try_can_fall_through = self._can_fall_through_statements_analysis(
            node.body
        )

        has_else = bool(node.orelse)

        if not try_can_fall_through and has_else:
            else_body = node.orelse
            self._report(
                name="else",
                first_node=else_body[0],
                last_node=else_body[-1],
                message="unreachable 'else' block",
            )

        any_except_can_fall_through = any(
            self._can_fall_through_statements_analysis(handler.body)
            for handler in node.handlers
        )

        statement_can_fall_through = (
            try_can_fall_through or any_except_can_fall_through
        )

        if not statement_can_fall_through:
            self._mark_as_no_fall_through(node)
