# TODO: Convert used_names and used_attrs to sets and use dedicated tests.
def check(items_or_names, expected_names):
    names = set(getattr(item, 'name', item) for item in items_or_names)
    assert names == set(expected_names)
