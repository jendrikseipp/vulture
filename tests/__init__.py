def check(items_or_names, expected_names):
    if isinstance(items_or_names, set):
        # items_or_names is a set of strings.
        assert items_or_names == set(expected_names)
    else:
        # items_or_names is a list of Item objects.
        assert set(item.name for item in items_or_names) == set(expected_names)
