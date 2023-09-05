import ast


class Reachability:
    def __init__(self, report):
        self.report = report
        self.no_fall_through_nodes = set()

    def reset(self):
        self.no_fall_through_nodes = set()

    def visit(self, node):
        if isinstance(node, (ast.Break, ast.Continue, ast.Return, ast.Raise)):
            self._mark_as_no_fall_through(node)
        elif isinstance(
            node,
            (
                ast.Module,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.While,
                ast.For,
                ast.AsyncFor,
                ast.With,
                ast.AsyncWith,
            ),
        ):
            self._can_fall_through_statements_analysis(node.body)
        elif isinstance(node, ast.If):
            self._handle_reachability_if(node)
        elif isinstance(node, ast.Try):
            self._handle_reachability_try(node)

    def _can_fall_through(self, node):
        return node not in self.no_fall_through_nodes

    def _mark_as_no_fall_through(self, node):
        self.no_fall_through_nodes.add(node)

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
                    self.report(
                        name=class_name,
                        first_node=next_sibling,
                        last_node=statements[-1],
                        message=f"unreachable code after '{class_name}'",
                        confidence=100,
                    )
                return False
        return True

    def _handle_reachability_if(self, node):

        if_can_fall_through = self._can_fall_through_statements_analysis(
            node.body
        )

        has_else = bool(node.orelse)

        if not has_else:
            else_can_fall_through = True
        else:
            else_can_fall_through = self._can_fall_through_statements_analysis(
                node.orelse
            )

        statement_can_fall_through = (
            if_can_fall_through or else_can_fall_through
        )

        if not statement_can_fall_through:
            self._mark_as_no_fall_through(node)

    def _handle_reachability_try(self, node):

        try_can_fall_through = self._can_fall_through_statements_analysis(
            node.body
        )

        has_else = bool(node.orelse)

        if not try_can_fall_through and has_else:
            else_body = node.orelse
            self.report(
                name="else",
                first_node=else_body[0],
                last_node=else_body[-1],
                message="unreachable 'else' block",
                confidence=100,
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
