import pytest


# from https://goodcode.io/articles/python-dict-object/
class objdict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)


def check_expected(f, test_inputs, expected_class, expected):
    if isinstance(expected, expected_class):
        assert f(*test_inputs) == expected
    else:
        with pytest.raises(expected):
            f(*test_inputs)
