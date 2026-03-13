import tokenize
from io import StringIO
from typing import List, Set


class AnnotationParser:
    def __init__(self, annotation_string: str):
        self._annotation = annotation_string

    def parse(self) -> Set[str]:
        type_names = set()
        token_generator = tokenize.generate_tokens(
            StringIO(self._annotation).readline
        )

        for token in token_generator:
            token_type = token.type
            token_string = token.string

            if token_type == tokenize.NAME:
                type_names.add(token_string)
            elif token_type == tokenize.STRING:
                for type_name in self._parse_string(token_string):
                    type_names.add(type_name)

        return type_names

    @staticmethod
    def _parse_string(token_string: str) -> List[str]:
        first_char = token_string[0]
        if first_char == "'" or first_char == '"':
            type_name = token_string[1:-1]
        else:
            type_name = token_string

        return type_name.split(".")
