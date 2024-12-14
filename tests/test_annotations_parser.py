import typing

import pytest

from vulture.annotation_parser import AnnotationParser


@pytest.mark.parametrize(
    "input_annotation, expected_types",
    [
        ("Foo", {"Foo"}),
        ("foo.Foo", {"foo", "Foo"}),
        ("List['Foo', 'Bar']", {"List", "Foo", "Bar"}),
        ('List["Foo", "Bar"]', {"List", "Foo", "Bar"}),
        ("List['foo.Foo', 'foo.Bar']", {"List", "foo", "Foo", "Bar"}),
    ],
)
def test_different_nested_annotations(
    input_annotation: str, expected_types: typing.Set[str]
):
    parser = AnnotationParser(input_annotation)
    assert parser.parse() == expected_types
