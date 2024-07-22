import mypy.api


def test_mypy():
    result = mypy.api.run(
        [
            "--check-untyped-defs",
            "--ignore-missing-imports",
            "--disable-error-code",
            "truthy-function",
            "--disable-error-code",
            "no-redef",
            "--disable-error-code",
            "attr-defined",
            "--disable-error-code",
            "misc",
            "./vulture",
        ]
    )
    assert result[0].startswith("Success: no issues found in ")
    assert result[1:] == ("", 0)
