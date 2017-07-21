# TODO: Convert used_vars and used_attrs to sets and use dedicated tests.
def check(asserted, assertion):
    names = set(getattr(item, 'name', item) for item in asserted)
    assert names == set(assertion)
