import pytest


def check_expected(f, test_inputs, expected_class, expected):
    if isinstance(expected, expected_class):
        assert f(*test_inputs) == expected
    else:
        with pytest.raises(expected):
            f(*test_inputs)
